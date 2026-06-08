<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Database\Eloquent\Model;

class Role extends Model
{
    use HasFactory;

    protected $guarded = [];

    /**
     * Relacija: Uloga ima više korisnika
     */
    public function users()
    {
        return $this->belongsToMany(User::class, 'role_user');
    }
}
