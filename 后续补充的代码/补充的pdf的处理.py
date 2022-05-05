import os
import multiprocessing
from termcolor import colored
import sys
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfparser import PDFParser
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice, TagExtractor
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import XMLConverter, HTMLConverter, TextConverter
from pdfminer.cmapdb import CMapDB
from pdfminer.layout import LAParams
from pdfminer.image import ImageWriter


def to_txt(argv):
    import getopt
    def usage():
        print(f'usage: {argv[0]} [-P password] [-o output] [-t text|html|xml|tag]'
               ' [-O output_dir] [-c encoding] [-s scale] [-R rotation]'
               ' [-Y normal|loose|exact] [-p pagenos] [-m maxpages]'
               ' [-S] [-C] [-n] [-A] [-V] [-M char_margin] [-L line_margin]'
               ' [-W word_margin] [-F boxes_flow] [-d] input.pdf ...')
        return 100
    try:
        (opts, args) = getopt.getopt(argv[1:], 'dP:o:t:O:c:s:R:Y:p:m:SCnAVM:W:L:F:')
    except getopt.GetoptError:
        return usage()
    if not args: return usage()
    # debug option
    debug = 0
    # input option
    password = b''
    pagenos = set()
    maxpages = 0
    # output option
    outfile = None
    outtype = None
    imagewriter = None
    rotation = 0
    stripcontrol = False
    layoutmode = 'normal'
    encoding = 'utf-8'
    pageno = 1
    scale = 1
    caching = True
    showpageno = True
    laparams = LAParams()
    for (k, v) in opts:
        if k == '-d': debug += 1
        elif k == '-P': password = v.encode('ascii')
        elif k == '-o': outfile = v
        elif k == '-t': outtype = v
        elif k == '-O': imagewriter = ImageWriter(v)
        elif k == '-c': encoding = v
        elif k == '-s': scale = float(v)
        elif k == '-R': rotation = int(v)
        elif k == '-Y': layoutmode = v
        elif k == '-p': pagenos.update( int(x)-1 for x in v.split(',') )
        elif k == '-m': maxpages = int(v)
        elif k == '-S': stripcontrol = True
        elif k == '-C': caching = False
        elif k == '-n': laparams = None
        elif k == '-A': laparams.all_texts = True
        elif k == '-V': laparams.detect_vertical = True
        elif k == '-M': laparams.char_margin = float(v)
        elif k == '-W': laparams.word_margin = float(v)
        elif k == '-L': laparams.line_margin = float(v)
        elif k == '-F': laparams.boxes_flow = float(v)
    #
    PDFDocument.debug = debug
    PDFParser.debug = debug
    CMapDB.debug = debug
    PDFPageInterpreter.debug = debug
    #
    rsrcmgr = PDFResourceManager(caching=caching)
    if not outtype:
        outtype = 'text'
        if outfile:
            if outfile.endswith('.htm') or outfile.endswith('.html'):
                outtype = 'html'
            elif outfile.endswith('.xml'):
                outtype = 'xml'
            elif outfile.endswith('.tag'):
                outtype = 'tag'
    if outfile:
        outfp = open(outfile, 'w', encoding=encoding)
    else:
        outfp = sys.stdout
    if outtype == 'text':
        device = TextConverter(rsrcmgr, outfp, laparams=laparams,
                               imagewriter=imagewriter)
    elif outtype == 'xml':
        device = XMLConverter(rsrcmgr, outfp, laparams=laparams,
                              imagewriter=imagewriter,
                              stripcontrol=stripcontrol)
    elif outtype == 'html':
        device = HTMLConverter(rsrcmgr, outfp, scale=scale,
                               layoutmode=layoutmode, laparams=laparams,
                               imagewriter=imagewriter, debug=debug)
    elif outtype == 'tag':
        device = TagExtractor(rsrcmgr, outfp)
    else:
        return usage()
    for fname in args:
        with open(fname, 'rb') as fp:
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            for page in PDFPage.get_pages(fp, pagenos,
                                          maxpages=maxpages, password=password,
                                          caching=caching, check_extractable=True):
                page.rotate = (page.rotate+rotation) % 360
                interpreter.process_page(page)
    device.close()
    outfp.close()
    return


def a_file(a_pdf_path, txt_dir, q):
    abs_txt_path = os.path.join(txt_dir, os.path.basename(a_pdf_path).replace(".PDF", ".txt"))
    try:
        to_txt(['', '-o', abs_txt_path, a_pdf_path])
    except:
        pass
    q.put(a_pdf_path)


if __name__ == '__main__':
    txt_save_path = r"./txt_save"
    pdf_path = r"C:\Users\Administrator\Desktop\new_pdfs"   # 这是姐下的那一千多个pdf
    pdf_names = os.listdir(pdf_path)
    os.makedirs(txt_save_path, exist_ok=True)

    pool = multiprocessing.Pool(3)
    queue = multiprocessing.Manager().Queue()
    for pdf_name in pdf_names:
        abs_pdf_path = os.path.join(pdf_path, pdf_name)
        pool.apply_async(a_file, args=(abs_pdf_path, txt_save_path, queue))

    num = 0
    while True:
        _ = queue.get()
        num += 1
        print(colored("\r进度：{:.2%}".format(num / len(pdf_names)), "red"), end="")
        if num == len(pdf_names):
            break
