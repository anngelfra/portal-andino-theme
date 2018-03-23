#! coding: utf-8
from ckan.lib import uploader
import os
import cgi
import pylons
import ckan.lib.munge as munge

from config_controller import GobArConfigController

config = pylons.config

_storage_path = None
_ufs = None

class GobArThemeResourceUploader(uploader.ResourceUpload):

    def __init__(self, data_dict):
        super(GobArThemeResourceUploader, self).__init__(data_dict)

        # Hacer el init para el ícono `icon_upload`

        path = self.get_storage_path()
        if not path:
            self.storage_path = None
            return
        self.storage_path = os.path.join(path, 'resources')
        try:
            os.makedirs(self.storage_path)
        except OSError, e:
            # errno 17 is file already exists
            if e.errno != 17:
                raise
        self.filename = None

        resource_id = data_dict.get('id')
        upload_field_storage = data_dict.pop('icon_upload', None)
        self.clear = data_dict.pop('clear_icon_upload', None)

        if isinstance(upload_field_storage, cgi.FieldStorage):
            self.filename = '%s-%s' % (resource_id, upload_field_storage.filename)
            self.upload_file = upload_field_storage.file

            data_dict['icon_url'] = '/user_images/%s' % self.filename
            data_dict['icon_url_type'] = 'upload'
        elif self.clear:
            data_dict['icon_url_type'] = ''

    def upload(self, id, max_size=10):
        super(GobArThemeResourceUploader, self).upload(id, max_size)

        if not self.storage_path or not self.filename:
            return

        # Hacer el upload para el ícono
        output_path = os.path.join(GobArConfigController.IMG_DIR, self.filename)
        output_file = open(output_path, 'wb')
        upload_file = self.upload_file
        upload_file.seek(0)
        while True:
            data = upload_file.read(2 ** 20)
            if not data:
                break
            output_file.write(data)
        output_file.close()
        return






    def get_storage_path(self):
        global _storage_path

        # None means it has not been set. False means not in config.
        if _storage_path is None:
            storage_path = config.get('ckan.storage_path')
            ofs_impl = config.get('ofs.impl')
            ofs_storage_dir = config.get('ofs.storage_dir')
            if storage_path:
                _storage_path = storage_path
            elif ofs_impl == 'pairtree' and ofs_storage_dir:
                _storage_path = ofs_storage_dir
                return _storage_path
            else:
                _storage_path = False

        return _storage_path
