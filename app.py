import os
import subprocess
import numpy as np
import re
import streamlit as st
from PIL import Image

# Ensure OpenCV loads correctly
os.environ["OPENCV_IO_MAX_IMAGE_PIXELS"] = str(2**40)  # Prevents large image issues

try:
    import cv2  # Import OpenCV
except ImportError:
    st.error("OpenCV is not installed correctly. Ensure OpenGL dependencies are available.")
    st.stop()

def install_tesseract():
    """Force install Tesseract OCR inside Streamlit Cloud."""
    st.warning("Tesseract is missing. Installing now...")
    subprocess.run(["sudo", "apt-get", "update"], check=True)
    subprocess.run(["sudo", "apt-get", "install", "-y", "tesseract-ocr", "tesseract-ocr-eng"], check=True)

try:
    import pytesseract  # Import Tesseract OCR

    # Check multiple possible paths for Tesseract
    possible_paths = ["/usr/bin/tesseract", "/usr/local/bin/tesseract"]
    tesseract_path = None
    
    for path in possible_paths:
        if os.path.exists(path):
            tesseract_path = path
            break

    if not tesseract_path:
        raise FileNotFoundError("Tesseract OCR is not installed. Installing now...")
    
    # Set the Tesseract path
    pytesseract.pytesseract.tesseract_cmd = tesseract_path

except (ImportError, FileNotFoundError):
    install_tesseract()  # Install Tesseract if missing
    import pytesseract  # Re-import after installation
    pytesseract.pytesseract.tesseract_cmd = "/usr/bin/tesseract"  # Set default path

st.title("Birth Certificate Verification System")
st.write("Upload a birth certificate image to verify its authenticity.")

uploaded_file = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])

def preprocess_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    sharpened = cv2.addWeighted(gray, 1.5, blurred, -0.5, 0)
    return sharpened

def extract_text(image):
    preprocessed_image = preprocess_image(image)
    text = pytesseract.image_to_string(preprocessed_image, config='--psm 6')
    return text

def detect_document_type(text):
    if "CERTIFICATE OF BIRTH" in text.upper():
        return "Certificate of Birth"
    elif "CERTIFIED TRANSCRIPT OF BIRTH" in text.upper():
        return "Certified Birth Transcript"
    elif "CERTIFICATE OF LIVE BIRTH" in text.upper():
        return "Certificate of Live Birth"
    else:
        return "Unknown Document Type"

def check_serial_number(text):
    match = re.search(r'\b[A-Z0-9]{7,12}\b', text)
    return match.group(0) if match else "Not Found"

def detect_seals_and_signatures(image):
    edges = cv2.Canny(image, 100, 200)
    edge_score = np.mean(edges)
    return "Seal/Signature Detected" if edge_score > 100 else "Seal/Signature Not Detected"

def pixelation_analysis(image):
    laplacian_var = cv2.Laplacian(image, cv2.CV_64F).var()
    if laplacian_var < 50:
        return f"High Pixelation Detected (Possible Tampering) - Score: {laplacian_var:.2f}"
    elif 50 <= laplacian_var < 100:
        return f"Moderate Pixelation - Score: {laplacian_var:.2f}"
    else:
        return f"Low Pixelation (Likely Authentic) - Score: {laplacian_var:.2f}"

if uploaded_file:
    image = Image.open(uploaded_file)
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    st.image(image, caption="Uploaded Image", use_container_width=True)

    extracted_text = extract_text(image_cv)
    document_type = detect_document_type(extracted_text)
    serial_number = check_serial_number(extracted_text)
    seal_status = detect_seals_and_signatures(image_cv)
    pixelation_result = pixelation_analysis(image_cv)

    confidence_score = 0
    if document_type != "Unknown Document Type":
        confidence_score += 3
    if serial_number != "Not Found":
        confidence_score += 2
    if "Detected" in seal_status:
        confidence_score += 3
    if "Low Pixelation" in pixelation_result:
        confidence_score += 2
    elif "Moderate Pixelation" in pixelation_result:
        confidence_score += 1

    if confidence_score >= 7:
        recommendation = "✅ Proceed - Document appears valid."
    elif 5 <= confidence_score < 7:
        recommendation = "⚠️ Hold for Further Review - Some inconsistencies detected."
    else:
        recommendation = "🚨 High Fraud Risk - Do not proceed without additional verification."

    st.subheader("Validation Report")
    st.markdown(f"""
    **Document Type:** {document_type}  
    **Serial Number:** {serial_number}  
    **Seal & Signature Detection:** {seal_status}  
    **Pixelation & Tampering Analysis:** {pixelation_result}  

    **Final Confidence Score:** {confidence_score}/10  
    **Recommendation:** {recommendation}  
    """)

    report_text = f"""
    Birth Certificate Validation Report

    Document Type: {document_type}
    Serial Number: {serial_number}
    Seal & Signature Detection: {seal_status}
    Pixelation & Tampering Analysis: {pixelation_result}

    Final Confidence Score: {confidence_score}/10
    Recommendation: {recommendation}
    """

    st.download_button(label="Download Report", data=report_text, file_name="validation_report.txt", mime="text/plain")

st.success("Web app ready. Run it locally or deploy!")
