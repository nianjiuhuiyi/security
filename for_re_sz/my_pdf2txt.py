# coding=utf-8
import os
import multiprocessing
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

"""
-P password : PDF password.
-o output : Output file name.
-t text|html|xml|tag : Output type. (default: automatically inferred from the output file name.)
-O output_dir : Output directory for extracted images.
    -c encoding : Output encoding. (default: utf-8)
-s scale : Output scale.
-R rotation : Rotates the page in degree.
-Y normal|loose|exact : Specifies the layout mode. (only for HTML output.)
-p pagenos : Processes certain pages only.
-m maxpages : Limits the number of maximum pages to process.
-S : Strips control characters.
-C : Disables resource caching.
-n : Disables layout analysis.
-A : Applies layout analysis for all texts including figures.
-V : Automatically detects vertical writing.
-M char_margin : Speficies the char margin.
-W word_margin : Speficies the word margin.
-L line_margin : Speficies the line margin.
-F boxes_flow : Speficies the box flow ratio.
-d : Turns on Debug output.
"""


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


def a_folder(pdf_dir, save_path):
    """
    针对一个文件夹(即一个上市公司)的处理
    @param pdf_dir: 类似于这样的地址：D:\SZ\temp_data\000002_万科A，里面是这个公司的所有报告
    @param save_path: 转的txt的最终保存地址，也是类似于这样：D:\SZ\temp_txt\000002_万科A
    """
    os.makedirs(save_path, exist_ok=True)
    pdf_files = os.listdir(pdf_dir)
    for pdf_name in pdf_files:
        txt_name = pdf_name.replace(".pdf", ".txt")
        abs_pdf_path = os.path.join(pdf_dir, pdf_name).replace("\\", "/")
        abs_txt_path = os.path.join(save_path, txt_name).replace("\\", "/")
        try:
            to_txt(['', '-o', abs_txt_path, abs_pdf_path])
        except Exception as e:
            pass
    print("{} 转换完毕！".format(os.path.basename(pdf_dir)))


if __name__ == '__main__':
    """
    这是第三步：把pdf转成txt
    """
    txt_save_path = r"D:\SZ\temp_txt"
    total_path = r"D:\SZ\temp_data"  # pdf总路径

    name_files = os.listdir(total_path)
    pool = multiprocessing.Pool(3)
    for com_code_name in name_files:
        save_path = os.path.join(txt_save_path, com_code_name)
        pdf_dir = os.path.join(total_path, com_code_name)
        pool.apply_async(a_folder, args=(pdf_dir, save_path))
    pool.close()
    pool.join()
    print("All is done!")

    # linux
    # txt_save_path = r"/home/songhui/sz_for_re/temp_txt"
    # total_path = r"/home/songhui/sz_for_re/temp_data"  # pdf总路径
    #
    # name_files = os.listdir(total_path)
    # pool = multiprocessing.Pool(35)
    # for com_code_name in name_files:
    #     save_path = os.path.join(txt_save_path, com_code_name)
    #     pdf_dir = os.path.join(total_path, com_code_name)
    #     pool.apply_async(a_folder, args=(pdf_dir, save_path))
    # pool.close()
    # pool.join()
    # print("All is done!")
