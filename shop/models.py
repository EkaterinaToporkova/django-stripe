from django.db import models


class Item(models.Model):
    CURRENCY_CHOICES = (
        ('usd', 'usd'),
        ('rub', 'rub')
    )

    name = models.CharField(max_length=255, verbose_name='product_name')
    code = models.CharField(max_length=255,
                            verbose_name='product_code')  # по этому полю различаем продукт (код продукта)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    unit = models.CharField(max_length=255, blank=True, null=True)  # единица измерения
    image_url = models.ImageField(upload_to='img_product')  # путь на изображение продукта
    note = models.TextField(blank=True, null=True)  # комментарий к продукту

    class Meta:  # все элементы отображаются по дате создания
        ordering = ['pk']

    def __str__(self):
        return f'name: {self.name}, price: {self.price},  image_url: {self.image_url}, pk: {self.code}'

    @property
    def price_unit(self):
        return int(self.price * 100)


class Product_image(models.Model):
    image = models.ImageField(upload_to='img_product')
    product = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='product_images')

    def __str__(self):
        return f'{self.product.name} image'


