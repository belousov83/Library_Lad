# Generated by Django 4.2.6 on 2023-10-13 11:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('books_app', '0003_alter_book_managers_alter_book_author_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookrate',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ratings', to='books_app.book'),
        ),
        migrations.AlterField(
            model_name='bookrate',
            name='rate',
            field=models.PositiveSmallIntegerField(choices=[(1, 'один'), (2, 'два'), (3, 'три'), (4, 'четыре'), (5, 'пять')], default=0),
        ),
        migrations.AlterField(
            model_name='comment',
            name='book',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='books_app.book'),
        ),
        migrations.AlterField(
            model_name='comment',
            name='visitor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments_visitor', to='books_app.visitor'),
        ),
        migrations.AlterUniqueTogether(
            name='bookrate',
            unique_together={('book', 'visitor')},
        ),
        migrations.RemoveField(
            model_name='bookrate',
            name='rated',
        ),
    ]