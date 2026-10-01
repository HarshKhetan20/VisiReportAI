import cv2
import numpy as np
import random
import os
from datetime import datetime, timezone
from jsonschema import validate, ValidationError
from fpdf import FPDF
from config import DEFECT_COLORS, DEFECT_DISPLAY_NAMES, VISIREPORT_SCHEMA

def generate_mock_audit_log() -> list:
    """Generate 5-8 historical entries for the audit log."""
    logs = []
    for i in range(random.randint(5, 8)):
        n_def = random.randint(0, 15)
        crit = sum([1 for _ in range(n_def) if random.random() > 0.8])
        logs.append({
            'TIMESTAMP': datetime.now(timezone.utc).isoformat(),
            'REPORT_ID': f"VR-20250428-10{i}0-A7F{i}",
            'BOARD_ID': f"PCBA-MED-00{random.randint(10,99)}",
            'TOTAL_DEFECTS': n_def,
            'CRITICAL': crit,
            'DISPOSITION': "NONCONFORMING" if n_def > 0 else "CONFORMING",
            'ENGINEER_ACTION': random.choice(["AUTO-GENERATED", "CONFIRMED", "OVERRIDDEN"]),
            'EXPORT_STATUS': "PDF EXPORTED ✓" if random.random() > 0.3 else "PENDING"
        })
    return logs

def run_yolo_inference(image: np.ndarray, model_path: str, conf_threshold: float) -> list[dict]:
    """Run actual YOLOv10 inference using ultralytics."""
    try:
        from ultralytics import YOLO
        model = YOLO(model_path)
    except Exception as e:
        print(f"Error loading model: {e}")
        return []

    # Run inference
    results = model(image, conf=conf_threshold)
    
    detections = []
    
    # Process results
    for i, box in enumerate(results[0].boxes):
        x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
        conf = float(box.conf[0].cpu().numpy())
        cls_id = int(box.cls[0].cpu().numpy())
        
        # Get class name
        cls_name = results[0].names[cls_id].lower()
        
        # Determine our class mapping
        if 'open' in cls_name: cls = 'open'
        elif 'short' in cls_name: cls = 'short'
        elif 'mousebite' in cls_name or 'mouse' in cls_name: cls = 'mousebite'
        elif 'spur' in cls_name: cls = 'spur'
        elif 'copper' in cls_name: cls = 'copper'
        elif 'pin' in cls_name or 'hole' in cls_name: cls = 'pin-hole'
        else: cls = 'spur' # fallback
        
        w = int(x2 - x1)
        h = int(y2 - y1)
        
        detections.append({
            'defect_id': f'VR-DEF-{i+1:04d}',
            'class': cls,
            'confidence': round(conf, 3),
            'global_bbox': {'x': int(x1), 'y': int(y1), 'w': w, 'h': h},
            'iso_severity': 'CRITICAL' if cls in ['open', 'short'] else ('MAJOR' if cls in ['mousebite', 'spur', 'pin-hole'] else 'MINOR'),
            'tile_origin': [0, 0],
            'status': '⏳ PENDING'
        })
    return detections

def run_mock_inference(image: np.ndarray, conf_threshold: float) -> list[dict]:
    """Generate realistic synthetic detections for demo purposes."""
    H, W = image.shape[:2]
    DEFECT_CLASSES = ['open', 'short', 'mousebite', 'spur', 'copper', 'pin-hole']
    n_defects = random.randint(4, 12)
    detections = []
    for i in range(n_defects):
        cls = random.choice(DEFECT_CLASSES)
        cx = random.randint(50, W-50)
        cy = random.randint(50, H-50)
        w = random.randint(20, 80)
        h = random.randint(20, 70)
        conf = random.uniform(conf_threshold + 0.05, 0.99)
        detections.append({
            'defect_id': f'VR-DEF-{i+1:04d}',
            'class': cls,
            'confidence': round(conf, 3),
            'global_bbox': {'x': max(0, cx - w//2), 'y': max(0, cy - h//2), 'w': w, 'h': h},
            'iso_severity': 'CRITICAL' if cls in ['open', 'short'] else ('MAJOR' if cls in ['mousebite', 'spur', 'pin-hole'] else 'MINOR'),
            'tile_origin': [random.randint(0,3), random.randint(0,3)],
            'status': '⏳ PENDING'
        })
    return detections

def validate_schema(payload: dict) -> bool:
    """Validate JSON payload against VISIREPORT_SCHEMA."""
    try:
        validate(instance=payload, schema=VISIREPORT_SCHEMA)
        return True
    except ValidationError:
        return False

def get_hex_to_bgr(hex_color: str) -> tuple:
    """Convert hex color string to BGR tuple for OpenCV."""
    hex_color = hex_color.lstrip('#')
    rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    return (rgb[2], rgb[1], rgb[0])  # Return BGR

def annotate_image(image: np.ndarray, detections: list) -> np.ndarray:
    """Draw bounding boxes and labels on the image using OpenCV."""
    img_copy = image.copy()
    for det in detections:
        x, y, w, h = det['global_bbox']['x'], det['global_bbox']['y'], det['global_bbox']['w'], det['global_bbox']['h']
        cls = det['class']
        conf = det['confidence']
        
        color_hex = DEFECT_COLORS.get(cls, '#FFFFFF')
        color_bgr = get_hex_to_bgr(color_hex)
        
        # Draw bounding box
        cv2.rectangle(img_copy, (x, y), (x+w, y+h), color_bgr, 2)
        
        # Label text
        label = f"{DEFECT_DISPLAY_NAMES.get(cls, cls).upper()} {conf:.1%}"
        (label_w, label_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
        
        # Draw label background
        overlay = img_copy.copy()
        cv2.rectangle(overlay, (x, max(0, y-label_h-10)), (x+label_w+10, y), color_bgr, -1)
        cv2.addWeighted(overlay, 0.7, img_copy, 0.3, 0, img_copy)
        
        # Draw label text
        cv2.putText(img_copy, label, (x+5, max(15, y-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
    return img_copy

def generate_pdf_report(report_id: str, board_id: str, date_str: str, disposition: str, defects: list, narrative: str) -> FPDF:
    """Generate ISO-13485 compliant PDF report using fpdf2."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Page 1: Header
    pdf.add_page()
    pdf.set_font("Courier", "B", 24)
    pdf.cell(0, 10, "VisiReport AI", ln=True, align="C")
    pdf.set_font("Courier", "", 12)
    pdf.cell(0, 10, "NON-CONFORMANCE REPORT", ln=True, align="C")
    pdf.ln(10)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(50, 10, "Report ID:")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, report_id, ln=True)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(50, 10, "Board ID:")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, board_id, ln=True)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(50, 10, "Inspection Date:")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, date_str, ln=True)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(50, 10, "Standard:")
    pdf.set_font("Helvetica", "", 12)
    pdf.cell(0, 10, "ISO 13485:2016 Clause 8.3 & 8.5.2", ln=True)
    
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(50, 10, "Disposition:")
    pdf.set_text_color(255, 59, 59) if disposition == "NONCONFORMING" else pdf.set_text_color(0, 230, 118)
    pdf.cell(0, 10, disposition, ln=True)
    pdf.set_text_color(0, 0, 0)
    
    # Page 2: Defect Registry
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Defect Registry", ln=True)
    pdf.ln(5)
    
    pdf.set_font("Helvetica", "B", 10)
    col_widths = [30, 35, 25, 30, 30, 40]
    headers = ["ID", "Class", "Conf.", "Coords(x,y)", "Severity", "Status"]
    for i, header in enumerate(headers):
        pdf.cell(col_widths[i], 10, header, border=1)
    pdf.ln()
    
    pdf.set_font("Helvetica", "", 9)
    for d in defects:
        pdf.cell(col_widths[0], 10, d['defect_id'], border=1)
        pdf.cell(col_widths[1], 10, d['class'].upper(), border=1)
        pdf.cell(col_widths[2], 10, f"{d['confidence']:.1%}", border=1)
        pdf.cell(col_widths[3], 10, f"{d['global_bbox']['x']},{d['global_bbox']['y']}", border=1)
        pdf.cell(col_widths[4], 10, d['iso_severity'], border=1)
        safe_status = d['status'].replace('⏳ ', '').replace('✅ ', '').replace('❌ ', '')
        pdf.cell(col_widths[5], 10, safe_status, border=1)
        pdf.ln()
    
    # Page 3: Narrative
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Cognitive Synthesis Narrative", ln=True)
    pdf.ln(5)
    pdf.set_font("Courier", "", 10)
    pdf.multi_cell(0, 6, narrative.encode('latin-1', 'replace').decode('latin-1'))
    
    # Page 4: CAPA
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(0, 10, "Corrective & Preventive Actions (CAPA)", ln=True)
    pdf.ln(5)
    pdf.set_font("Helvetica", "", 11)
    capa_text = """
1. [IMMEDIATE] Quarantine batch lot #PCB-042-B. Do not release to downstream assembly.
2. [ROOT CAUSE] Audit SMT paste application settings. Re-calibrate squeegee pressure.
3. [PREVENTIVE] Implement automated solder paste inspection (SPI) at post-print stage.
    """
    pdf.multi_cell(0, 8, capa_text)
    
    pdf.ln(30)
    pdf.cell(0, 10, "___________________________________________________", ln=True)
    pdf.cell(0, 10, "Quality Assurance Engineer Signature", ln=True)
    
    return pdf
