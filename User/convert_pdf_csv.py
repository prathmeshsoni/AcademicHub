import os

import pandas as pd
import requests

BASE_URL_LOCAL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class PdfToCsv:
    def __init__(self, SourceFile, DestinationFile, index_count, request):
        api_key_list = [
            'hajugi@cyclelove.cc_vYw1y9WKN3F68TJxteCeGO3u8QxA8gA70744r3J3R632cs95XSNl9LfM8Tc5nSeH'
        ]
        self.API_KEY = api_key_list[index_count]
        self.SourceFile = SourceFile
        self.DestinationFile = DestinationFile
        self.BASE_URL = "https://api.pdf.co/v1"
        self.Pages = ""
        self.Password = ""
        self.request = request

    def main(self):
        uploadedFileUrl = self.uploadFile()
        if uploadedFileUrl is not None:
            result = self.convertPdfToCSV(uploadedFileUrl)
        else:
            result = None
        return result

    def convertPdfToCSV(self, uploadedFileUrl):
        """Converts PDF To CSV using PDF.co Web API"""

        destinationFile = self.DestinationFile
        API_KEY = self.API_KEY
        Pages = self.Pages
        Password = self.Password
        BASE_URL = self.BASE_URL

        parameters = {
            "name": os.path.basename(destinationFile),
            "password": Password,
            "pages": Pages,
            "url": uploadedFileUrl
        }

        # Prepare URL for 'PDF To CSV' API request
        url = "{}/pdf/convert/to/csv".format(BASE_URL)

        # Execute request and get response as JSON
        response = requests.post(url, data=parameters, headers={"x-api-key": API_KEY})
        if response.status_code == 200:
            json = response.json()

            if not json["error"]:
                #  Get URL of result file
                resultFileUrl = json["url"]
                # Download result file
                r = requests.get(resultFileUrl, stream=True)
                if r.status_code == 200:
                    with open(destinationFile, 'wb') as file:
                        for chunk in r:
                            file.write(chunk)

                    self.print_log('Convert File Success')
                    return 200

                else:
                    self.print_log(f'{response.status_code} {response.reason} | Download Request error')
            else:
                self.print_log(f'{json["message"]} | Json Msg')
        else:
            self.print_log(f'{response.status_code} {response.reason} | Execute Request error')

        return response.status_code

    def uploadFile(self):
        """Uploads file to the cloud"""
        fileName = self.SourceFile
        BASE_URL = self.BASE_URL
        API_KEY = self.API_KEY
        # 1. RETRIEVE PRESIGNED URL TO UPLOAD FILE.

        # Prepare URL for 'Get Presigned URL' API request
        url = "{}/file/upload/get-presigned-url?contenttype=application/octet-stream&name={}".format(
            BASE_URL, os.path.basename(fileName))

        # Execute request and get response as JSON
        response = requests.get(url, headers={"x-api-key": API_KEY})
        if response.status_code == 200:
            json = response.json()

            if not json["error"]:
                # URL to use for file upload
                uploadUrl = json["presignedUrl"]
                # URL for future reference
                uploadedFileUrl = json["url"]

                # 2. UPLOAD FILE TO CLOUD.
                with open(fileName, 'rb') as file:
                    requests.put(uploadUrl, data=file,
                                 headers={"x-api-key": API_KEY, "content-type": "application/octet-stream"})

                return uploadedFileUrl
            else:
                # Show service reported error
                self.print_log(f'{json["message"]} | Service Json Msg')
        else:
            self.print_log(f'{response.status_code} {response.reason} | Main Upload Request error')

        return None

    def print_log(self, text):
        from .views import logger
        logger(self.request, '', f'{text}', filename_s='pdf_to_csv')
        if self.request.session.get('enrollment'):
            logger(self.request, self.request.session.get('enrollment'), text)
        else:
            logger(self.request, '', f'See:{text}')


class Final_csv:
    def __init__(self, pdf_name_1, names, index_count, request):
        self.pdf_name = pdf_name_1
        self.names = names
        self.index_count = index_count
        self.request = request
        self.loggs = PdfToCsv('', '', 0, request)

    def get_content(self, check, check_1):
        pdf_name_1 = self.pdf_name
        index_count = self.index_count

        temp_path = f'{BASE_URL_LOCAL}/uploads/pdf'
        if not os.path.exists(temp_path):
            os.makedirs(temp_path)

        names = f'{temp_path}/{self.names}.csv'
        if check == 1:
            if os.path.exists(names):
                os.remove(names)
            try:
                check = PdfToCsv(pdf_name_1, names, index_count, self.request).main()
                self.loggs.print_log(f'{check} | Status')
            except Exception as e:
                self.loggs.print_log(f'{e} | Error Found')
            if check == 503:
                return None, None, 'fail', 1
            elif check == 401:
                return None, None, None, 1
            elif not check:
                return None, None, None, 1

            pdf_name_1 = names
            names = f'{temp_path}/final_{self.names}.csv'
            if os.path.exists(names):
                os.remove(names)

        if check == 2:
            with open(self.names, 'r') as f:
                lines = f.read()

            contact_list = []
            for i in lines.split('\n'):
                cc = i.split('-')
                items = {
                    'enroll': f'{cc[0]}',
                    'contact': f'{cc[1]}',
                }
                contact_list.append(items)
            return contact_list

        else:
            names = f'{temp_path}/final_{self.names}.csv'
            if os.path.exists(names):
                os.remove(names)

        logss = self.loggs
        logss.print_log(f'{os.path.basename(pdf_name_1)} | Start Getting Content')
        try:
            df = pd.read_csv(pdf_name_1, encoding='utf-8')
        except Exception as e:
            logss.print_log(f'Error to read csv file:{e} | df Error')
            return self.error_save(pdf_name_1, names)

        headers = []
        try:
            for k in df.items():
                key = k[0]
                headers.append(key)
        except:
            pass

        logss.print_log(f'{len(headers)} | headers len')

        if check_1 == 0:
            f_list = []
            x_list = []
            if len(headers) == 10 or len(headers) == 11 or len(headers) == 12 or len(headers) == 13:
                for i in df.index:
                    try:
                        if i <= df.__len__():
                            try:
                                int(df[headers[1]][i])
                            except:
                                continue

                            enroll = df[headers[1]][i]
                            if str(df[headers[3]][i]) == 'nan':
                                div = df[headers[3]][i - 1]
                            else:
                                div = df[headers[3]][i]
                            if str(df[headers[3]][i]) == 'nan':
                                _branch = df[headers[2]][i - 1]
                            else:
                                _branch = df[headers[2]][i]
                            name = df[headers[4]][i]
                            if str(df[headers[6]][i]) == 'nan':
                                sec_1 = df[headers[6]][i - 1]
                            else:
                                sec_1 = df[headers[6]][i]
                            if str(df[headers[7]][i]) == 'nan':
                                sec_2 = df[headers[7]][i - 1]
                            else:
                                sec_2 = df[headers[7]][i]
                            try:
                                _totall = int(sec_1) + int(sec_2)
                            except:
                                _totall = 0
                            no_ = len(x_list) + 1
                            s = [
                                f'{no_}',
                                f'{enroll}',
                                '',
                                f'{div}',
                                f'{name}',
                                '',
                                f'{sec_1}',
                                f'{sec_2}',
                                '',
                            ]

                            items = {
                                'no': f'{no_}',
                                'enroll': f'{enroll}',
                                'branch': f'{_branch}',
                                'div': f'{div}',
                                'name': f'{name}',
                                'section_1': f'{sec_1}',
                                'section_2': f'{sec_2}',
                                'total': f'{_totall}',
                            }
                            self.save_item(items, names)
                            x_list.append(items)
                            f_list.append(tuple(s))
                    except:
                        pass

            elif len(headers) == 9:
                for i in df.index:
                    try:
                        enroll = df[headers[1]][i]
                        try:
                            int(enroll)
                            if len(f'{enroll}') != 12:
                                continue
                        except:
                            continue
                        div = df[headers[3]][i]
                        _branch = df[headers[2]][i]
                        name = df[headers[4]][i]
                        sec_1 = df[headers[6]][i]
                        sec_2 = df[headers[7]][i]
                        try:
                            _totall = int(sec_1) + int(sec_2)
                        except:
                            _totall = 0
                        no_ = len(x_list) + 1
                        s = [
                            f'{no_}',
                            f'{enroll}',
                            '',
                            f'{div}',
                            f'{name}',
                            '',
                            f'{sec_1}',
                            f'{sec_2}',
                            '',
                        ]

                        items = {
                            'no': f'{no_}',
                            'enroll': f'{enroll}',
                            'branch': f'{_branch}',
                            'div': f'{div}',
                            'name': f'{name}',
                            'section_1': f'{sec_1}',
                            'section_2': f'{sec_2}',
                            'total': f'{_totall}',
                        }
                        self.save_item(items, names)
                        x_list.append(items)
                        f_list.append(tuple(s))
                    except:
                        pass

            elif len(headers) == 8:
                for i in df.index:
                    try:
                        if i <= df.__len__():
                            enroll = df[headers[1]][i]
                            try:
                                int(enroll)
                                if len(f'{enroll}') != 12:
                                    continue
                            except:
                                continue
                            div = df[headers[3]][i]
                            _branch = df[headers[2]][i]
                            name = df[headers[4]][i]
                            sec_1 = df[headers[5]][i]
                            sec_2 = df[headers[6]][i]
                            try:
                                _totall = int(sec_1) + int(sec_2)
                            except:
                                _totall = 0
                            no_ = len(x_list) + 1
                            s = [
                                f'{no_}',
                                f'{enroll}',
                                '',
                                f'{div}',
                                f'{name}',
                                '',
                                f'{sec_1}',
                                f'{sec_2}',
                                '',
                            ]

                            items = {
                                'no': f'{no_}',
                                'enroll': f'{enroll}',
                                'branch': f'{_branch}',
                                'div': f'{div}',
                                'name': f'{name}',
                                'section_1': f'{sec_1}',
                                'section_2': f'{sec_2}',
                                'total': f'{_totall}',
                            }
                            self.save_item(items, names)
                            x_list.append(items)
                            f_list.append(tuple(s))
                    except:
                        pass

            else:
                for i in df.index:
                    try:
                        if type(i) == int:
                            try:
                                s = [
                                    f'{i + 1}',
                                    f"{df['enroll'][i]}",
                                    '',
                                    f"{df['div'][i]}",
                                    f"{df['name'][i]}",
                                    '',
                                    f"{df['Section 1'][i]}",
                                    f"{df['Section 2'][i]}",
                                    '',
                                ]
                                try:
                                    _totall = int(df['Section 1'][i]) + int(df['Section 2'][i])
                                except:
                                    _totall = 0
                                try:
                                    items = {
                                        'no': f'{i + 1}',
                                        'enroll': f"{df['enroll'][i]}",
                                        'branch': '',
                                        'div': f"{df['div'][i]}",
                                        'name': f"{df['name'][i]}",
                                        'section_1': f"{df['Section 1'][i]}",
                                        'section_2': f"{df['Section 2'][i]}",
                                        'total': f'{_totall}',
                                    }
                                    x_list.append(items)
                                    self.save_item(items, names)

                                except:
                                    pass
                                f_list.append(tuple(s))
                            except:
                                pass
                        else:
                            try:
                                int(f'{i[1]}')
                            except:
                                continue
                            f_list.append(i)
                            try:
                                items = {
                                    'no': f'{i[0]}',
                                    'enroll': f'{i[1]}',
                                    'branch': f'{i[2]}',
                                    'div': f'{i[3]}',
                                    'name': f'{i[4]}',
                                    'section_1': f'{i[6]}',
                                    'section_2': f'{i[7]}',
                                    'total': f'{i[8]}',
                                }
                                self.save_item(items, names)
                                x_list.append(items)
                            except:
                                pass
                    except:
                        pass

            s_name = f'pdf/final_{self.names}.csv'

        else:
            f_list = []
            x_list = []
            if len(headers) == 10:
                for i in df.index:
                    try:
                        if i <= df.__len__():
                            try:
                                int(f'{df[headers[1]][i]}')
                            except:
                                continue

                            enroll = df[headers[1]][i]
                            if str(df[headers[3]][i]) == 'nan':
                                div = df[headers[3]][i - 1]
                            else:
                                div = df[headers[3]][i]
                            if str(df[headers[3]][i]) == 'nan':
                                _branch = df[headers[2]][i - 1]
                            else:
                                _branch = df[headers[2]][i]
                            name = df[headers[4]][i]
                            if str(df[headers[6]][i]) == 'nan':
                                sec_1 = df[headers[6]][i - 1]
                            else:
                                sec_1 = df[headers[6]][i]
                            if str(df[headers[7]][i]) == 'nan':
                                sec_2 = df[headers[7]][i - 1]
                            else:
                                sec_2 = df[headers[7]][i]
                            try:
                                _totall = int(sec_1) + int(sec_2)
                            except:
                                _totall = 0
                            no_ = len(x_list) + 1
                            s = [
                                f'{no_}',
                                f'{enroll}',
                                '',
                                f'{div}',
                                f'{name}',
                                '',
                                f'{sec_1}',
                                f'{sec_2}',
                                '',
                            ]

                            items = {
                                'no': f'{no_}',
                                'enroll': f'{enroll}',
                                'branch': f'{_branch}',
                                'div': f'{div}',
                                'name': f'{name}',
                                'section_1': f'{sec_1}',
                                'section_2': f'{sec_2}',
                                'total': f'{_totall}',
                            }
                            self.save_item(items, names)
                            x_list.append(items)
                            f_list.append(tuple(s))
                    except:
                        pass

            elif len(headers) == 9:
                for i in df.index:
                    try:
                        enroll = df[headers[1]][i]
                        try:
                            int(enroll)
                            if len(f'{enroll}') != 12:
                                continue
                        except:
                            continue
                        div = df[headers[3]][i]
                        _branch = df[headers[2]][i]
                        name = df[headers[4]][i]
                        sec_1 = df[headers[6]][i]
                        sec_2 = df[headers[7]][i]
                        try:
                            _totall = int(sec_1) + int(sec_2)
                        except:
                            _totall = 0
                        no_ = len(x_list) + 1
                        s = [
                            f'{no_}',
                            f'{enroll}',
                            '',
                            f'{div}',
                            f'{name}',
                            '',
                            f'{sec_1}',
                            f'{sec_2}',
                            '',
                        ]

                        items = {
                            'no': f'{no_}',
                            'enroll': f'{enroll}',
                            'branch': f'{_branch}',
                            'div': f'{div}',
                            'name': f'{name}',
                            'section_1': f'{sec_1}',
                            'section_2': f'{sec_2}',
                            'total': f'{_totall}',
                        }
                        self.save_item(items, names)
                        x_list.append(items)
                        f_list.append(tuple(s))
                    except:
                        pass

            elif len(headers) == 8 or len(headers) == 9:
                for i in df.index:
                    try:
                        if i <= df.__len__():
                            enroll = df[headers[1]][i]
                            try:
                                int(enroll)
                                if len(f'{enroll}') != 12:
                                    continue
                            except:
                                continue
                            div = df[headers[3]][i]
                            _branch = df[headers[2]][i]
                            name = df[headers[4]][i]
                            sec_1 = df[headers[5]][i]
                            sec_2 = df[headers[6]][i]
                            try:
                                _totall = int(sec_1) + int(sec_2)
                            except:
                                _totall = 0
                            no_ = len(x_list) + 1
                            s = [
                                f'{no_}',
                                f'{enroll}',
                                f'{div}',
                                f'{name}',
                            ]

                            items = {
                                'no': f'{no_}',
                                'enroll': f'{enroll}',
                                'branch': f'{_branch}',
                                'div': f'{div}',
                                'name': f'{name}',
                            }
                            self.save_item(items, names)
                            x_list.append(items)
                            f_list.append(tuple(s))
                    except:
                        pass

            else:
                for i in df.index:
                    try:
                        if type(i) == int:
                            try:
                                s = [
                                    f'{i + 1}',
                                    f"{df['enroll'][i]}",
                                    '',
                                    f"{df['div'][i]}",
                                    f"{df['name'][i]}",
                                    '',
                                    f"{df['Section 1'][i]}",
                                    f"{df['Section 2'][i]}",
                                    '',
                                ]
                                try:
                                    _totall = int(df['Section 1'][i]) + int(df['Section 2'][i])
                                except:
                                    _totall = 0
                                try:
                                    items = {
                                        'no': f'{i + 1}',
                                        'enroll': f"{df['enroll'][i]}",
                                        'branch': '',
                                        'div': f"{df['div'][i]}",
                                        'name': f"{df['name'][i]}",
                                        'section_1': f"{df['Section 1'][i]}",
                                        'section_2': f"{df['Section 2'][i]}",
                                        'total': f'{_totall}',
                                    }
                                    x_list.append(items)
                                    self.save_item(items, names)

                                except:
                                    pass
                                f_list.append(tuple(s))
                            except:
                                pass
                        else:
                            try:
                                int(f'{i[1]}')
                            except:
                                continue
                            f_list.append(i)
                            try:
                                items = {
                                    'no': f'{i[0]}',
                                    'enroll': f'{i[1]}',
                                    'branch': f'{i[2]}',
                                    'div': f'{i[3]}',
                                    'name': f'{i[4]}',
                                    'section_1': f'{i[6]}',
                                    'section_2': f'{i[7]}',
                                    'total': f'{i[8]}',
                                }
                                self.save_item(items, names)
                                x_list.append(items)
                            except:
                                pass
                    except:
                        pass

            s_name = f'pdf/final_{self.names}.csv'

        if not f_list:
            logss.print_log(f'some error to extract')

        logss.print_log(f'{os.path.basename(pdf_name_1)} | End Getting Content')

        return x_list, f_list, s_name, 0

    def error_save(self, pdf_name, names):
        try:
            df = pd.read_csv(pdf_name, encoding='utf-8', delimiter='\t')
        except:
            return None, None, None, 0

        f_list = []
        x_list = []
        for i in range(df.__len__()):
            a = df.iloc[i, 0].split(',')
            enroll = f'{a[1]}'.replace('"', '').strip()
            try:
                int(enroll)
                if len(f'{enroll}') != 12:
                    continue
            except:
                continue
            div = f'{a[3]}'.replace('"', '').strip()
            _branch = f'{a[2]}'.replace('"', '').strip()
            name = f'{a[4]}'.replace('"', '').strip()
            if len(a) == 10:
                try:
                    sec_1 = int(f'{a[6]}'.replace('"', '').strip())
                except:
                    sec_1 = 0
                try:
                    sec_2 = int(f'{a[7]}'.replace('"', '').strip())
                except:
                    sec_2 = 0
            else:
                try:
                    sec_1 = int(f'{a[7]}'.replace('"', '').strip())
                except:
                    sec_1 = 0
                try:
                    sec_2 = int(f'{a[8]}'.replace('"', '').strip())
                except:
                    sec_2 = 0

            _totall = int(sec_1) + int(sec_2)

            no_ = len(x_list) + 1
            s = [
                f'{no_}',
                f'{enroll}',
                '',
                f'{div}',
                f'{name}',
                '',
                f'{sec_1}',
                f'{sec_2}',
                '',
            ]

            items = {
                'no': f'{no_}',
                'enroll': f'{enroll}',
                'branch': f'{_branch}',
                'div': f'{div}',
                'name': f'{name}',
                'section_1': f'{sec_1}',
                'section_2': f'{sec_2}',
                'total': f'{_totall}',
            }
            self.save_item(items, names)
            x_list.append(items)
            f_list.append(tuple(s))

        s_name = f'pdf/final_{self.names}.csv'

        return x_list, f_list, s_name, 0

    def save_item(self, item, names):
        pass_file = names
        df = pd.DataFrame([item])
        if os.path.exists(pass_file):
            df.to_csv(pass_file, index=False, header=False, mode='a')
        else:
            df.to_csv(pass_file, index=False, header=True, mode='a')
