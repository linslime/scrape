import os
import csv

def get_string_name(num):
    if num < 10:
        return '00' + str(num)
    elif num < 100:
        return '0' + str(num)
    else:
        return str(num)

def get_image_index_directory(comics_name, chapter_index, image_index):
    return './comics/' + comics_name + '/images/' + get_string_name(chapter_index) + '/' + get_string_name(image_index) + '.jpg'

def get_chapter_index_directory(comics_name, chapter_index):
    return './comics/' + comics_name + '/images/' + get_string_name(chapter_index)

def get_pdf_directory(comics_name):
    return './comics/' + comics_name + '/pdf'

def get_pdf_file_directory(comics_name, chapter_index):
    return get_pdf_directory(comics_name) + '/' + get_string_name(chapter_index) + '.pdf'

def get_pdf_gap_directory(comics_name):
    return './comics/' + comics_name + '/pdf_gap'

def get_pdf_gap_file_directory(comics_name, chapter_index):
    return get_pdf_gap_directory(comics_name) + '/' + get_string_name(chapter_index) + '.pdf'

def get_aggregate_pdf_directory(comics_name):
    return './comics/' + comics_name + '/' + comics_name + '.pdf'

def get_image_urls_csv_directory(comics_name):
    return './comics/' + comics_name + '/' + comics_name + '.csv'

def get_chapter_image_directories(comics_name, chapter_index):
    image_names = os.listdir(get_chapter_index_directory(comics_name, chapter_index))
    return [get_chapter_index_directory(comics_name, chapter_index) + '/' + image_name for image_name in image_names]

def get_chapter_pdf_directory(comics_name):
    pdf_names = os.listdir(get_pdf_directory(comics_name))
    return [get_pdf_directory(comics_name) + '/' + pdf_name for pdf_name in pdf_names]

def init_comics_directory(comics_name, chapter_number):
    for chapter_index in range(chapter_number):
        if not os.path.exists(get_chapter_index_directory(comics_name, chapter_index)):
            os.makedirs(get_chapter_index_directory(comics_name, chapter_index))
    if not os.path.exists(get_pdf_directory(comics_name)):
        os.makedirs(get_pdf_directory(comics_name))
    if not os.path.exists(get_pdf_gap_directory(comics_name)):
        os.makedirs(get_pdf_gap_directory(comics_name))

def init_image_urls(comics_name, chapter_number):
    if not os.path.exists(get_image_urls_csv_directory(comics_name)):
        return [[] for i in range(chapter_number)]
    image_urls = []
    with open(get_image_urls_csv_directory(comics_name), 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            image_urls.append(row)
    if len(image_urls) < chapter_number:
        image_urls += [[] for i in range(chapter_number - len(image_urls))]
    return image_urls

def init_images_and_pdf(comics_name, image_urls):
    images_exist = [[0 for i in urls] for urls in image_urls]
    pdfs_exist = [0 for urls in image_urls]
    aggregate_pdf_exist = 0
    for chapter in range(len(image_urls)):
        for image_number in range(len(image_urls[chapter])):
            if os.path.exists(get_image_index_directory(comics_name, chapter, image_number)):
                images_exist[chapter][image_number] = 1
    for chapter in range(len(image_urls)):
        if os.path.exists(get_pdf_file_directory(comics_name, chapter)):
            pdfs_exist[chapter] = 1
    if sum(pdfs_exist) == len(pdfs_exist):
        aggregate_pdf_exist = 1
    return images_exist, pdfs_exist, aggregate_pdf_exist

def save_image(comics_name, chapter_index, image_index, image):
    with open(get_image_index_directory(comics_name, chapter_index, image_index), 'wb') as file:
        file.write(image)
    file.close()

def save_image_urls_csv(comics_name, csv_file):
    file = open(get_image_urls_csv_directory(comics_name), 'w', newline='')
    csv.writer(file).writerows(csv_file)
    file.close()

def save_pdf(comics_name, chapter_index, pdf):
    with open(get_pdf_file_directory(comics_name, chapter_index), 'wb') as file:
        pdf.write(file)
    file.close()

def save_pdf_gap(comics_name, chapter_index, pdf):
    with open(get_pdf_gap_file_directory(comics_name, chapter_index), 'wb') as file:
        file.write(pdf)
    file.close()

def save_aggregate_pdf(comics_name, pdf):
    with open(get_aggregate_pdf_directory(comics_name), 'wb') as file:
        file.write(pdf)
    file.close()