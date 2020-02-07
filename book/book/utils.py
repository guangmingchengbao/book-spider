from Crypto.Util.Padding import pad, unpad
from Crypto.Cipher import AES
import os, random, struct, base64, io, sys, math, requests, img2pdf, re, hashlib, os
import numpy as np
from PIL import Image, ImageStat, ImageFilter
from urllib.parse import unquote
from scrapy.utils.python import to_bytes


WITH_PDFRW = True
if WITH_PDFRW:
    try:
        from pdfrw import PdfDict, PdfName
    except ImportError:
        PdfDict = img2pdf.MyPdfDict
        PdfName = img2pdf.MyPdfName
        WITH_PDFRW = False
else:
    PdfDict = img2pdf.MyPdfDict
    PdfName = img2pdf.MyPdfName


class AESCipher:

    def __init__(self, key):
        self.key = key

    def encrypt(self, raw):
        """加密"""
        raw = pad(raw.encode('utf-8'), 16)
        cipher = AES.new(self.key, AES.MODE_ECB)
        return base64.b64encode(cipher.encrypt(raw)) 

    def decrypt(self, enc):
        """解密"""
        enc = base64.b64decode(enc)
        cipher = AES.new(self.key, AES.MODE_ECB)
        return unpad(cipher.decrypt(enc), 16).decode('utf-8')
    
    def encrypt_file(self, in_filename, out_filename, chunksize=64*1024):
        """加密文件"""
        if not out_filename:
            out_filename = in_filename + '.enc'
        
        cipher = AES.new(self.key, AES.MODE_ECB)
        filesize = os.path.getsize(in_filename)

        with open(in_filename, 'rb') as infile:
            with open(out_filename, 'wb') as outfile:
                outfile.write(struct.pack('<Q', filesize))
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    elif len(chunk) % 16 != 0:
                        chunk += ' ' * (16 - len(chunk) % 16)
                    outfile.write(cipher.encrypt(chunk))

    def decrypt_file(self, in_filename, out_filename=None, chunksize=24*1024):
        """解密文件"""
        if not out_filename:
            out_filename = os.path.splitext(in_filename)[0]

        with open(in_filename, 'rb') as infile:
            cipher = AES.new(self.key, AES.MODE_ECB)
            with open(out_filename, 'wb') as outfile:
                while True:
                    chunk = infile.read(chunksize)
                    if len(chunk) == 0:
                        break
                    outfile.write(cipher.decrypt(chunk))

    def decrypt_body(self, body):
        """解密响应消息体"""
        cipher = AES.new(self.key, AES.MODE_ECB)
        return cipher.decrypt(body)


class WQXueTang:
    session = requests.Session()
    _PIXWEIGHT = np.concatenate((np.arange(128, 0, -1), np.arange(0, 128))) / 128

    def __init__(self):
        super().__init__()

    @classmethod
    def login(self):
        url = 'http://open.izhixue.cn/checklogin?response_type=code&client_id=wqxuetang&redirect_uri=https%3A%2F%2Fwww.wqxuetang.com%2Fv1%2Flogin%2Fcallbackwq&scope=userinfo&state=https%3A%2F%2Flib-nuanxin.wqxuetang.com%2F%23%2F'
        r = self.session.post(url, data = { 'account': 'zomco@sina.com', 'password': 'w42ndGF0115' })
        data = r.json()
        if data['code'] != '0':
            print('Login failed: {}({})'.format(data['message'], data['code']))
            return False
        self.session.get(unquote(data['data']), verify=False)
        return True

    @classmethod
    def get_cookies(self):
        cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
        if not 'PHPSESSID' in cookies:
            self.login()
            cookies = requests.utils.dict_from_cookiejar(self.session.cookies)
        print(cookies)
        return cookies
    
    @classmethod
    def generate_pdf(self, item):
        media_guid = hashlib.sha1(to_bytes('https://lib-nuanxin.wqxuetang.com/page/img/{}'.format(item['id']))).hexdigest()
        media_base = 'wqxuetang/extra'
        media_out = '{}/{}.pdf'.format(media_base, media_guid)
        if not os.path.exists(media_base):
            os.makedirs(media_base)
        with open(media_out, "wb") as f:
            self.pdf_convert(
                ['{}/{}'.format(media_base, n['path']) for n in item['files']],
                title=item['name'],
                author=item['author'],
                with_pdfrw=True,
                contents=item['extra'],
                outputstream=f
            )
        return True, media_out
    
    def generate_pdf_outline(self, pdf, contents, parent=None):
        if parent is None:
            parent = PdfDict(indirect=True)
        if not contents:
            return parent
        first = prev = None
        for k, row in enumerate(contents):
            try:
                page = pdf.writer.pagearray[int(row['pnum'])-1]
            except IndexError:
                # bad bookmark
                continue
            bookmark = PdfDict(
                Parent=parent,
                Title=row['label'],
                A=PdfDict(
                    D=[page, PdfName.Fit],
                    S=PdfName.GoTo
                ),
                indirect=True
            )
            children = row.get('children')
            if children:
                bookmark = generate_pdf_outline(pdf, children, bookmark)
            if first:
                bookmark[PdfName.Prev] = prev
                prev[PdfName.Next] = bookmark
            else:
                first = bookmark
            prev = bookmark
        parent[PdfName.Count] = k + 1
        parent[PdfName.First] = first
        parent[PdfName.Last] = prev
        return parent

    def pdf_convert(self, *images, **kwargs):
        _default_kwargs = dict(
            title=None,
            author=None,
            creator=None,
            producer=None,
            creationdate=None,
            moddate=None,
            subject=None,
            keywords=None,
            colorspace=None,
            contents=None,
            nodate=False,
            layout_fun=img2pdf.default_layout_fun,
            viewer_panes=None,
            viewer_initial_page=None,
            viewer_magnification=None,
            viewer_page_layout=None,
            viewer_fit_window=False,
            viewer_center_window=False,
            viewer_fullscreen=False,
            with_pdfrw=True,
            first_frame_only=False,
            allow_oversized=True,
        )
        for kwname, default in _default_kwargs.items():
            if kwname not in kwargs:
                kwargs[kwname] = default

        pdf = img2pdf.pdfdoc(
            "1.3",
            kwargs["title"],
            kwargs["author"],
            kwargs["creator"],
            kwargs["producer"],
            kwargs["creationdate"],
            kwargs["moddate"],
            kwargs["subject"],
            kwargs["keywords"],
            kwargs["nodate"],
            kwargs["viewer_panes"],
            kwargs["viewer_initial_page"],
            kwargs["viewer_magnification"],
            kwargs["viewer_page_layout"],
            kwargs["viewer_fit_window"],
            kwargs["viewer_center_window"],
            kwargs["viewer_fullscreen"],
            kwargs["with_pdfrw"],
        )

        # backwards compatibility with older img2pdf versions where the first
        # argument to the function had to be given as a list
        if len(images) == 1:
            # if only one argument was given and it is a list, expand it
            if isinstance(images[0], (list, tuple)):
                images = images[0]

        if not isinstance(images, (list, tuple)):
            images = [images]

        for img in images:
            # img is allowed to be a path, a binary string representing image data
            # or a file-like object (really anything that implements read())
            try:
                rawdata = img.read()
            except AttributeError:
                if not isinstance(img, (str, bytes)):
                    raise TypeError("Neither implements read() nor is str or bytes")
                # the thing doesn't have a read() function, so try if we can treat
                # it as a file name
                try:
                    with open(img, "rb") as f:
                        rawdata = f.read()
                except Exception:
                    # whatever the exception is (string could contain NUL
                    # characters or the path could just not exist) it's not a file
                    # name so we now try treating it as raw image content
                    rawdata = img

            for (
                color,
                ndpi,
                imgformat,
                imgdata,
                imgwidthpx,
                imgheightpx,
                palette,
                inverted,
                depth,
                rotation,
            ) in img2pdf.read_images(rawdata, kwargs["colorspace"], kwargs["first_frame_only"]):
                pagewidth, pageheight, imgwidthpdf, imgheightpdf = kwargs["layout_fun"](
                    imgwidthpx, imgheightpx, ndpi
                )

                userunit = None
                if pagewidth < 3.00 or pageheight < 3.00:
                    logging.warning(
                        "pdf width or height is below 3.00 - too " "small for some viewers!"
                    )
                elif pagewidth > 14400.0 or pageheight > 14400.0:
                    if kwargs["allow_oversized"]:
                        userunit = img2pdf.find_scale(pagewidth, pageheight)
                        pagewidth /= userunit
                        pageheight /= userunit
                        imgwidthpdf /= userunit
                        imgheightpdf /= userunit
                    else:
                        raise img2pdf.PdfTooLargeError(
                            "pdf width or height must not exceed 200 inches."
                        )
                # the image is always centered on the page
                imgxpdf = (pagewidth - imgwidthpdf) / 2.0
                imgypdf = (pageheight - imgheightpdf) / 2.0
                pdf.add_imagepage(
                    color,
                    imgwidthpx,
                    imgheightpx,
                    imgformat,
                    imgdata,
                    imgwidthpdf,
                    imgheightpdf,
                    imgxpdf,
                    imgypdf,
                    pagewidth,
                    pageheight,
                    userunit,
                    palette,
                    inverted,
                    depth,
                    rotation,
                )

        if kwargs['contents']:
            if pdf.with_pdfrw:
                catalog = pdf.writer.trailer.Root
            else:
                catalog = pdf.writer.catalog
            catalog[PdfName.Outlines] = self.generate_pdf_outline(pdf, kwargs['contents'])

        if kwargs["outputstream"]:
            pdf.tostream(kwargs["outputstream"])
            return

        return pdf.tostring()

    def otsu_threshold(self, hist):
        total = sum(hist)
        sumB = 0
        wB = 0
        maximum = 0.0
        sum1 = np.dot(np.arange(256), hist)
        for i in range(256):
            wB += hist[i]
            wF = total - wB
            if wB == 0 or wF == 0:
                continue
            sumB += i * hist[i]
            mF = (sum1 - sumB) / wF
            between = wB * wF * ((sumB / wB) - mF) * ((sumB / wB) - mF)
            if between >= maximum:
                level = i + 1
                maximum = between
        return level

    def auto_downgrade(self, pil_img, thumb_size=128, grey_cutoff=1, bw_ratio=0.99):
        mode = pil_img.mode
        if mode == '1' and mode not in ('L', 'LA', 'RGB', 'RGBA'):
            # ignore special modes
            return pil_img
        elif mode == 'P':
            pil_img = pil_img.convert('RGB')
        elif mode == 'PA':
            pil_img = pil_img.convert('RGBA')
        bands = pil_img.getbands()
        alpha_band = False
        if bands[-1] == 'A':
            alpha_band = True
            if all(x == 255 for x in pil_img.getdata(len(bands) - 1)):
                alpha_band = False
        if bands[:3] == ('R', 'G', 'B'):
            thumb = pil_img.resize((thumb_size,thumb_size), resample=Image.BILINEAR)
            pixels = np.array(thumb.getdata(), dtype=float)[:, :3]
            pixels_max = np.max(pixels, axis=1)
            pixels_min = np.min(pixels, axis=1)
            val = np.mean(pixels_max - pixels_min)
            if val > grey_cutoff:
                if bands[-1] == 'A' and not alpha_band:
                    return pil_img.convert('RGB')
                else:
                    return pil_img
            if alpha_band:
                return pil_img.convert('LA')
            else:
                pil_img = pil_img.convert('L')
        if alpha_band:
            return pil_img
        hist = pil_img.histogram()[:256]
        if np.average(self._PIXWEIGHT, weights=hist) > bw_ratio:
            #threshold = self.otsu_threshold(hist)
            #pil_img = pil_img.point(lambda p: p > threshold and 255)
            return pil_img.convert('1', dither=Image.NONE)
        if bands[-1] == 'A':
            return pil_img.convert('L')
        return pil_img

    def auto_encode(self, fp, quality=95, thumb_size=128, grey_cutoff=1, bw_ratio=0.99):
        if isinstance(fp, str):
            with open(fp, 'rb') as f:
                orig_data = f.read()
        elif isinstance(fp, bytes):
            orig_data = fp
        else:
            orig_data = fp.read()
        orig_buf = io.BytesIO(orig_data)
        orig_size = len(orig_data)
        im = Image.open(orig_buf)
        out_im = auto_downgrade(im, thumb_size, grey_cutoff, bw_ratio)
        buf = io.BytesIO()
        if out_im.mode == '1':
            out_im.save(buf, 'TIFF', compression='group4')
            return buf.getvalue(), 'TIFF'
        elif out_im.mode[0] == 'L' or out_im.mode[-1] == 'A':
            out_im.save(buf, 'PNG', optimize=True)
            return buf.getvalue(), 'PNG'
        if im.format.startswith('JPEG'):
            out_format = 'PNG'
            out_im.save(buf, 'PNG', optimize=True)
        else:
            out_format = 'JPEG'
            out_im.convert('RGB').save(buf, 'JPEG', quality=95, optimize=True)
        out_data = buf.getvalue()
        if len(out_data) > orig_size:
            if out_im.mode == im.mode:
                return orig_data, im.format
            else:
                buf = io.BytesIO()
                out_im.save(buf, 'PNG', optimize=True)
                return buf.getvalue(), 'PNG'
        else:
            return out_data, out_format