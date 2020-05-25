# -*- coding:utf-8 -*-
__doc__ = "oss文件相关"

import oss2


class FileOss(object):
    def __init__(self, AccessKey_ID, AccessKeySecret, OssHost, OssBucket, OssPath, UrlTimeout):
        self.AccessKey_ID = AccessKey_ID
        self.AccessKeySecret = AccessKeySecret
        self.OssHost = OssHost
        self.OssBucket = OssBucket
        self.UrlTimeout = UrlTimeout
        self.OssPath = OssPath
        self.auth = oss2.Auth(self.AccessKey_ID, self.AccessKeySecret)
        self.bucket = oss2.Bucket(self.auth, self.OssHost, self.OssBucket)

    def upload(self, filename, file):
        """

        :param filename: 文件名称
        :param path:    文件储存路径
        :return:
        """
        self.bucket.put_object(self.OssPath + filename, file)
        exist = self.bucket.object_exists(self.OssPath + filename)
        if exist:
            return filename
        else:
            return None

    def file_exist(self, filename):
        exist = self.bucket.object_exists(self.OssPath + filename)
        return exist

    def sign_url(self, filename, expires):
        try:
            exist = self.bucket.object_exists(self.OssPath + filename)
            if exist:
                if expires:
                    url = self.bucket.sign_url('GET', self.OssPath + filename, expires)
                else:
                    url = self.bucket.sign_url('GET', self.OssPath + filename, self.UrlTimeout)
                return url
            else:
                return None
        except:
            return None

    def delete_file(self, filename):
        self.bucket.delete_object(self.OssPath + filename)

    def get_file(self, filename, path):
        self.bucket.get_object_to_file(self.OssPath + filename, path)
