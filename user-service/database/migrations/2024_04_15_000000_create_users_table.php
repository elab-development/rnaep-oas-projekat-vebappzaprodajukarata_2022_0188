<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * Pravi tabele za User servis sa PasswordReset
     */
    public function up(): void
    {
        // Tabela korisnika
        Schema::create('users', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('email')->unique();
            $table->string('password');
            $table->timestamp('email_verified_at')->nullable();
            $table->rememberToken();
            $table->timestamps();

            // Indeksi
            $table->index('email');
            $table->index('created_at');
        });

        // Tabela uloga
        Schema::create('roles', function (Blueprint $table) {
            $table->id();
            $table->string('name')->unique(); // 'guest', 'user', 'admin'
            $table->string('description')->nullable();
            $table->timestamps();
        });

        // Pivot tabela za mnogo-prema-mnogom relaciju
        Schema::create('role_user', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained('users')->onDelete('cascade');
            $table->foreignId('role_id')->constrained('roles')->onDelete('cascade');
            $table->timestamps();

            // Sprečava duplo dodelu iste uloge
            $table->unique(['user_id', 'role_id']);

            // Indeksi
            $table->index('user_id');
            $table->index('role_id');
        });

        // Sanctum API tokens tabela
        Schema::create('personal_access_tokens', function (Blueprint $table) {
            $table->id();
            $table->morphs('tokenable');
            $table->string('name');
            $table->string('token', 64)->unique();
            $table->text('abilities')->nullable();
            $table->timestamp('last_used_at')->nullable();
            $table->timestamp('expires_at')->nullable();
            $table->timestamps();

            // Indeksi
            $table->index('tokenable_type');
            $table->index('tokenable_id');
        });

        // ✨ NOVA: Password Reset tabela
        Schema::create('password_resets', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained('users')->onDelete('cascade');
            $table->string('reset_token')->unique(); // Unikalni token za reset
            $table->timestamp('expires_at'); // Kada ističe token (npr. 1 sat)
            $table->timestamp('used_at')->nullable(); // Kada je token korišćen
            $table->timestamps();

            // Indeksi
            $table->index('user_id');
            $table->index('reset_token');
            $table->index('expires_at');
        });
    }

    /**
     * Vraća migracije unazad
     */
    public function down(): void
    {
        Schema::dropIfExists('password_resets');
        Schema::dropIfExists('personal_access_tokens');
        Schema::dropIfExists('role_user');
        Schema::dropIfExists('roles');
        Schema::dropIfExists('users');
    }
};
