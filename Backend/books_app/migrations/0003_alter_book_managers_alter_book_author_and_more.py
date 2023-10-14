# Generated by Django 4.2.6 on 2023-10-12 17:53

import books_app.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import mptt.fields


class Migration(migrations.Migration):

    dependencies = [
        ('books_app', '0002_bookcomment_visitor_images_bookrate_bookitem_and_more'),
    ]

    operations = [
        migrations.AlterModelManagers(
            name='book',
            managers=[
                ('custom', django.db.models.manager.Manager()),
            ],
        ),
        migrations.AlterField(
            model_name='book',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='books_app.author', verbose_name='Автор'),
        ),
        migrations.AlterField(
            model_name='book',
            name='description',
            field=models.TextField(blank=True, verbose_name='Краткое описание'),
        ),
        migrations.AlterField(
            model_name='book',
            name='name',
            field=models.CharField(max_length=100, verbose_name='Название книги'),
        ),
        migrations.AlterField(
            model_name='book',
            name='year',
            field=models.PositiveSmallIntegerField(verbose_name='Год издания'),
        ),
        migrations.AlterField(
            model_name='images',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=books_app.models.get_image_filename, validators=[django.core.validators.FileExtensionValidator(allowed_extensions=('png', 'jpg', 'webp', 'jpeg', 'gif'))], verbose_name='Изовражение'),
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('comment', models.TextField(blank=True, max_length=500)),
                ('published_at', models.DateTimeField(auto_now_add=True)),
                ('lft', models.PositiveIntegerField(editable=False)),
                ('rght', models.PositiveIntegerField(editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(editable=False)),
                ('book', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='book_comment', to='books_app.book')),
                ('parent', mptt.fields.TreeForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='books_app.comment', verbose_name='Родительский комментарий')),
                ('visitor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='visitor_comment', to='books_app.visitor')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.AlterField(
            model_name='bookitem',
            name='comments',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='comments_item', to='books_app.comment'),
        ),
        migrations.DeleteModel(
            name='BookComment',
        ),
    ]
