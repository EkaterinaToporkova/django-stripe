from django.db import models


class Item(models.Model):
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


class Product_image(models.Model):
    image = models.ImageField(upload_to='img_product')
    product = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='product_images')

    def __str__(self):
        return f'{self.product.name} image'


class OrderDetail(models.Model):
    id = models.BigAutoField(primary_key=True)
    customer_email = models.EmailField(verbose_name='Customer Email')
    product = models.ForeignKey(to=Item, verbose_name='Item', on_delete=models.PROTECT)
    amount = models.IntegerField(verbose_name='amount')
    stripe_payment_intent = models.CharField(max_length=200)
    # This field can be changed as status
    has_paid = models.BooleanField(default=False, verbose_name='payment status')
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)
