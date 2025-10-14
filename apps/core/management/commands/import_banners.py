"""
Management command to import existing banner images from static folder to database
"""
import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File
from apps.core.models import BannerImage


class Command(BaseCommand):
    help = 'Import existing banner images from static folder to database'

    def handle(self, *args, **options):
        # Path to static banner images
        static_banner_path = os.path.join(settings.BASE_DIR, 'static', 'images', 'banner')

        # Path to media banners folder
        media_banner_path = os.path.join(settings.MEDIA_ROOT, 'banners')

        # Create media banners directory if it doesn't exist
        os.makedirs(media_banner_path, exist_ok=True)

        # Banner image files
        banner_files = [
            {'filename': 'banner.jpeg', 'title': 'Welcome to GiftTree - Banner 1'},
            {'filename': 'banner2.jpg', 'title': 'Special Offers - Banner 2'},
            {'filename': 'banner3.jpg', 'title': 'Best Gifts - Banner 3'},
            {'filename': 'banner4.jpg', 'title': 'Exclusive Collection - Banner 4'},
        ]

        created_count = 0
        skipped_count = 0

        for idx, banner_info in enumerate(banner_files, start=1):
            filename = banner_info['filename']
            title = banner_info['title']

            # Check if banner already exists
            if BannerImage.objects.filter(title=title).exists():
                self.stdout.write(
                    self.style.WARNING(f'Banner "{title}" already exists. Skipping...')
                )
                skipped_count += 1
                continue

            # Source file path
            source_path = os.path.join(static_banner_path, filename)

            if not os.path.exists(source_path):
                self.stdout.write(
                    self.style.ERROR(f'File not found: {source_path}')
                )
                continue

            # Destination file path in media
            dest_filename = f'banner_{idx}{os.path.splitext(filename)[1]}'
            dest_path = os.path.join(media_banner_path, dest_filename)

            # Copy file to media folder
            shutil.copy2(source_path, dest_path)

            # Create BannerImage instance
            with open(dest_path, 'rb') as f:
                banner = BannerImage(
                    title=title,
                    sort_order=idx,
                    is_active=True
                )
                banner.image.save(dest_filename, File(f), save=True)

            created_count += 1
            self.stdout.write(
                self.style.SUCCESS(f'Successfully imported: {title}')
            )

        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\n=== Import Summary ==='
                f'\nCreated: {created_count}'
                f'\nSkipped: {skipped_count}'
                f'\nTotal: {created_count + skipped_count}'
            )
        )

        # Display admin instructions
        self.stdout.write(
            self.style.WARNING(
                f'\n\nTo manage banners:'
                f'\n1. Go to Django Admin: /admin/'
                f'\n2. Navigate to "Core" > "Banner Images"'
                f'\n3. You can add, edit, or delete banners'
                f'\n4. Change sort_order to reorder banners'
                f'\n5. Toggle is_active to show/hide banners'
            )
        )
