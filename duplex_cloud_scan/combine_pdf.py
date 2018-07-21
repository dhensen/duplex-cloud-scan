from pdfrw import PdfReader, PdfWriter


def combine_two_pdfs(front, back, output_file):
    front_pages = PdfReader(front).pages
    back_pages = PdfReader(back).pages
    back_pages = reversed(back_pages)
    combined = [None] * (len(front_pages) + len(front_pages))
    combined[::2] = front_pages
    combined[1::2] = back_pages

    writer = PdfWriter(output_file)
    for page in combined:
        writer.addpage(page)
    writer.write()


if __name__ == '__main__':
    combine_two_pdfs('example_pdfs/front.pdf', 'example_pdfs/back.pdf',
                     'example_pdfs/combined.pdf')
