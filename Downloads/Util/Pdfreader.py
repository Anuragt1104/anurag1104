import PyPDF2

class PDFFileReader:
    @staticmethod
    def read_pdf_file_line_by_line(file_path):
        lines = []
        with open(file_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfFileReader(pdf_file)
            for page_num in range(pdf_reader.numPages):
                page = pdf_reader.getPage(page_num)
                lines.extend(page.extractText().split('\n'))
        return lines

# Example usage
if __name__ == "__main__":
    file_path = '/path/to/your/pdf/file.pdf'  # Specify the path to your PDF file
    lines = PDFFileReader.read_pdf_file_line_by_line(file_path)
    for line in lines:
        print(line)
