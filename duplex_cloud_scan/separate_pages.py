from pdfrw import PdfReader, PdfWriter

from duplex_cloud_scan.logger import get_logger

logger = get_logger(__name__)


def separate_pages(input_file, output_folder):
    logger.debug(f'input_file={input_file}')
    pages = PdfReader(input_file).pages

    i = 0
    for page in pages:
        i += 1
        output_file = f'{output_folder}/file_{i}.pdf'
        logger.debug(f'output_file_{i}={output_file}')
        writer = PdfWriter()
        writer.addpage(page)
        writer.write(fname=output_file)
    logger.debug(f'{i} pdf pages written in separate files')


if __name__ == '__main__':
    separate_pages('example_pdfs/separate/20190331223041_001.pdf',
                   'example_pdfs/separate')
