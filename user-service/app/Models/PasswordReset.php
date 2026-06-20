<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class PasswordReset extends Model
{
    use HasFactory;

    protected $table = 'password_resets';
    protected $guarded = [];

    /**
     * Kastovanje atributa
     */
    protected $casts = [
        'expires_at' => 'datetime',
        'used_at' => 'datetime',
    ];

    /**
     * Relacija: Reset pripada korisniku
     */
    public function user()
    {
        return $this->belongsTo(User::class);
    }

    /**
     * Proverava da li je token još uvek validan
     */
    public function isValid(): bool
    {
        // Token mora biti nekorišćen i nije istekao
        return $this->used_at === null && $this->expires_at > now();
    }

    /**
     * Označava token kao korišćen
     */
    public function markAsUsed(): void
    {
        $this->update(['used_at' => now()]);
    }
}
