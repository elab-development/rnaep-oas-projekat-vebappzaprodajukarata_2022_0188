<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Laravel\Sanctum\HasApiTokens;

class User extends Authenticatable
{
    use HasFactory, Notifiable, HasApiTokens;

    /**
     * Atributi koji nisu masovno dodelivi
     *
     * @var array<int, string>
     */
    protected $guarded = [];

    /**
     * Atributi koji se kriju od serijalizacije
     *
     * @var array<int, string>
     */
    protected $hidden = [
        'password',
    ];

    /**
     * Atributi sa kastovanjem tipova
     *
     * @var array<string, string>
     */
    protected $casts = [
        'email_verified_at' => 'datetime',
        'password' => 'hashed',
    ];

    /**
     * Relacija: Korisnik ima više uloga
     */
    public function roles()
    {
        return $this->belongsToMany(Role::class, 'role_user');
    }

    /**
     * ✨ NOVA: Relacija - Korisnik ima više password reset tokena
     */
    public function passwordResets()
    {
        return $this->hasMany(PasswordReset::class);
    }

    /**
     * Pronalazi aktivne password reset tokene
     */
    public function getActivePasswordReset()
    {
        return $this->passwordResets()
                    ->where('used_at', null)
                    ->where('expires_at', '>', now())
                    ->first();
    }

    /**
     * Proverava da li korisnik ima određenu ulogu
     *
     * @param string $roleName
     * @return bool
     */
    public function hasRole($roleName)
    {
        return $this->roles()->where('name', $roleName)->exists();
    }

    /**
     * Proverava da li korisnik ima neku od zadatih uloga
     *
     * @param array $roleNames
     * @return bool
     */
    public function hasAnyRole($roleNames)
    {
        return $this->roles()->whereIn('name', $roleNames)->exists();
    }

    /**
     * Dodeljuje ulogu korisniku
     *
     * @param string $roleName
     * @return void
     */
    public function assignRole($roleName)
    {
        $role = Role::where('name', $roleName)->first();
        
        if ($role && !$this->hasRole($roleName)) {
            $this->roles()->attach($role);
        }
    }

    /**
     * Uklanja ulogu korisniku
     *
     * @param string $roleName
     * @return void
     */
    public function removeRole($roleName)
    {
        $role = Role::where('name', $roleName)->first();
        
        if ($role) {
            $this->roles()->detach($role);
        }
    }

    /**
     * Vraća uloge kao niz string-ova
     *
     * @return array
     */
    public function getRoleNames()
    {
        return $this->roles()->pluck('name')->toArray();
    }

    /**
     * Vraća sve podatke korisnika (bez lozinke)
     *
     * @return array
     */
    public function toArray()
    {
        return [
            'id' => $this->id,
            'name' => $this->name,
            'email' => $this->email,
            'roles' => $this->getRoleNames(),
            'created_at' => $this->created_at,
            'updated_at' => $this->updated_at,
        ];
    }
}
