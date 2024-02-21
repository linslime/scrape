import img2pdf
from PyPDF2.generic import RectangleObject
from PyPDF2 import PdfReader, PdfWriter, Transformation, PdfMerger
from FileDirectoryManagement import *

def create_pdf(comics_name, chapter_index):
    write_content = img2pdf.convert(get_chapter_image_directories(comics_name, chapter_index))
    save_pdf_gap(comics_name, chapter_index, write_content)

    reader = PdfReader(get_pdf_gap_file_directory(comics_name, chapter_index))
    writer = PdfWriter()
    index = 0
    total_page = reader.pages[index]
    while True:
        index += 1
        if index < len(reader.pages):
            if total_page.cropbox.width == reader.pages[index].cropbox.width:
                page = reader.pages[index]
                total_page = merge_pdf_bottom(total_page, page)
            else:
                writer.add_page(total_page)
                total_page = reader.pages[index]
        else:
            writer.add_page(total_page)
            break

    save_pdf(comics_name, chapter_index, writer)

def create_aggregate_pdf(comics_name):
    file_merger = PdfMerger()
    paths = get_chapter_pdf_directory(comics_name)
    for pdf in paths:
        file_merger.append(pdf)
    file_merger.write(get_aggregate_pdf_directory(comics_name))

def merge_pdf_bottom(page2, page1):
        height = page1.cropbox.height
        op = Transformation().translate(tx=0, ty=height)  # 拼接在下方
        page2.add_transformation(op)
        cb = page2.cropbox

        page2.mediabox = RectangleObject((cb.left, cb.bottom + height, cb.right, cb.top + height))
        page2.cropbox = RectangleObject((cb.left, cb.bottom + height, cb.right, cb.top + height))
        page2.trimbox = RectangleObject((cb.left, cb.bottom + height, cb.right, cb.top + height))
        page2.bleedbox = RectangleObject((cb.left, cb.bottom + height, cb.right, cb.top + height))
        page2.artbox = RectangleObject((cb.left, cb.bottom + height, cb.right, cb.top + height))

        page1.merge_page(page2, expand=True)
        mb = page1.mediabox
        page1.mediabox = RectangleObject((mb.left, mb.bottom, mb.right, mb.top))
        page1.cropbox = RectangleObject((mb.left, mb.bottom, mb.right, mb.top))
        page1.trimbox = RectangleObject((mb.left, mb.bottom, mb.right, mb.top))
        page1.bleedbox = RectangleObject((mb.left, mb.bottom, mb.right, mb.top))
        page1.artbox = RectangleObject((mb.left, mb.bottom, mb.right, mb.top))

        return page1
