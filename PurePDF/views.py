from django.shortcuts import render
from django.http import FileResponse
from django.views.decorators.csrf import csrf_exempt
from pypdf import PdfMerger, PdfReader, PdfWriter
from PIL import Image
from io import BytesIO
import fitz


def home(request):
    if request.method == 'POST':
        tool = request.POST.get('tool')
        uploaded_files = request.FILES.getlist('files')

        if not tool or not uploaded_files:
            return render(request, 'home.html', {'error': 'Please select a tool and upload file(s).'})

        if tool == 'compress':
            output = compress_pdf(uploaded_files[0])
            return FileResponse(output, as_attachment=True, filename='pure_compressed.pdf')

        elif tool == 'merge':
            writer = PdfWriter()
            for f in uploaded_files:
                reader = PdfReader(f)
                for page in reader.pages:
                    writer.add_page(page)

            output = BytesIO()
            writer.write(output)
            output.seek(0)
            return FileResponse(output, as_attachment=True, filename='pure_merged.pdf')
        
        elif tool == 'image-to-pdf':
            images = []
            for f in uploaded_files:
                img = Image.open(f)
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                images.append(img)

            pdf_buffer = BytesIO()
            images[0].save(pdf_buffer, format='PDF', save_all=True, append_images=images[1:])
            pdf_buffer.seek(0)
            return FileResponse(pdf_buffer, as_attachment=True, filename='pure_converted.pdf')

        else:
            return render(request, 'home.html', {'error': 'Invalid tool selected.'})
    return render(request, 'home.html')


def compress_pdf(file):
    doc = fitz.open(stream=file.read(), filetype="pdf")
    new_doc = fitz.open()

    dpi = 100  # control output quality
    for page in doc:
        # Render the page to an image
        pix = page.get_pixmap(dpi=dpi, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Compress the image
        img_io = BytesIO()
        img.save(img_io, format="JPEG", quality=50)  # Adjust quality here
        img_io.seek(0)

        # Get PDF page size in points (1 point = 1/72 inch)
        width_pt = pix.width * 72 / dpi
        height_pt = pix.height * 72 / dpi
        rect = fitz.Rect(0, 0, width_pt, height_pt)

        # Create new page and insert full image (no cropping)
        new_page = new_doc.new_page(width=width_pt, height=height_pt)
        new_page.insert_image(rect, stream=img_io.read())

    output = BytesIO()
    new_doc.save(output, deflate=True, garbage=4)
    new_doc.close()
    output.seek(0)
    return output