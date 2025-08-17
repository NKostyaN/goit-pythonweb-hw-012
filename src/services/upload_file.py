import cloudinary
import cloudinary.uploader


class UploadFileService:
    def __init__(self, cloud_name, api_key, api_secret):
        """
        Ініціалізація сервісу для завантаження файлів на Cloudinary.

        Аргументи:
            cloud_name: Ім'я хмари в Cloudinary.
            api_key: API ключ для доступу до Cloudinary.
            api_secret: API секрет для доступу до Cloudinary.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username) -> str:
        """
        Завантаження файла на Cloudinary і генерація URL для доступу до зображення.

        Аргументи:
            file: Файл для завантаження.
            username: Ім'я користувача для формування унікального public_id.

        Повертає:
            str: URL зображення, доступного на Cloudinary.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
