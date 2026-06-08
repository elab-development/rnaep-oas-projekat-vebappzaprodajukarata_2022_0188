FROM php:8.2-fpm

# Instaliraj sistemske zavisnosti
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip

# Očisti cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Instaliraj PHP ekstenzije
RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd

# Instaliraj Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Postavi radni direktorijum
WORKDIR /var/www

# Kopira aplikaciju
COPY . /var/www

# Instaliraj zavisnosti
RUN composer install --no-interaction --optimize-autoloader

# Postavi dozvole
RUN chown -R www-data:www-data /var/www \
    && chmod -R 755 /var/www/storage

EXPOSE 9000

CMD ["php-fpm"]
