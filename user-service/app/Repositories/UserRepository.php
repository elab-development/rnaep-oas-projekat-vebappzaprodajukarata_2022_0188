<?php

namespace App\Repositories;

use App\Models\User;
use Illuminate\Pagination\Paginator;

class UserRepository
{
    /**
     * Pronalazi korisnika po ID-u
     *
     * @param int $id
     * @return User|null
     */
    public function findById(int $id): ?User
    {
        return User::find($id);
    }

    /**
     * Pronalazi korisnika po email-u
     *
     * @param string $email
     * @return User|null
     */
    public function findByEmail(string $email): ?User
    {
        return User::where('email', $email)->first();
    }

    /**
     * Pronalazi sve korisnike sa paginacijom
     *
     * @param int $perPage
     * @return Paginator
     */
    public function all(int $perPage = 15)
    {
        return User::paginate($perPage);
    }

    /**
     * Pronalazi korisnike po ulozi
     *
     * @param string $roleName
     * @return \Illuminate\Database\Eloquent\Collection
     */
    public function findByRole(string $roleName)
    {
        return User::whereHas('roles', function ($query) use ($roleName) {
            $query->where('name', $roleName);
        })->get();
    }

    /**
     * Kreira novog korisnika
     *
     * @param array $data
     * @return User
     */
    public function create(array $data): User
    {
        return User::create($data);
    }

    /**
     * Ažurira korisnika
     *
     * @param int $id
     * @param array $data
     * @return User|null
     */
    public function update(int $id, array $data): ?User
    {
        $user = $this->findById($id);
        
        if (!$user) {
            return null;
        }

        $user->update($data);
        return $user;
    }

    /**
     * Briše korisnika
     *
     * @param int $id
     * @return bool
     */
    public function delete(int $id): bool
    {
        $user = $this->findById($id);
        
        if (!$user) {
            return false;
        }

        return $user->delete();
    }

    /**
     * Pronalazi korisnike sa pretraživanjem
     *
     * @param string $searchTerm
     * @param int $perPage
     * @return Paginator
     */
    public function search(string $searchTerm, int $perPage = 15)
    {
        return User::where('name', 'LIKE', "%{$searchTerm}%")
                   ->orWhere('email', 'LIKE', "%{$searchTerm}%")
                   ->paginate($perPage);
    }

    /**
     * Broji sve korisnike
     *
     * @return int
     */
    public function count(): int
    {
        return User::count();
    }

    /**
     * Proverava da li email postoji
     *
     * @param string $email
     * @param int $excludeUserId (ID korisnika koji se isključuje iz provere)
     * @return bool
     */
    public function emailExists(string $email, int $excludeUserId = null): bool
    {
        $query = User::where('email', $email);
        
        if ($excludeUserId) {
            $query->where('id', '!=', $excludeUserId);
        }
        
        return $query->exists();
    }

    /**
     * Pronalazi sve adminine
     *
     * @return \Illuminate\Database\Eloquent\Collection
     */
    public function getAdmins()
    {
        return $this->findByRole('admin');
    }

    /**
     * Pronalazi sve obične korisnike (ne-adminine)
     *
     * @return \Illuminate\Database\Eloquent\Collection
     */
    public function getRegularUsers()
    {
        return $this->findByRole('user');
    }

    /**
     * Pronalazi sve goste
     *
     * @return \Illuminate\Database\Eloquent\Collection
     */
    public function getGuests()
    {
        return $this->findByRole('guest');
    }

    /**
     * Dobija sve uloge korisnika
     *
     * @param int $userId
     * @return array
     */
    public function getUserRoles(int $userId): array
    {
        $user = $this->findById($userId);
        return $user ? $user->getRoleNames() : [];
    }

    /**
     * Dodeljuje rolu korisniku
     *
     * @param int $userId
     * @param string $roleName
     * @return bool
     */
    public function assignRole(int $userId, string $roleName): bool
    {
        $user = $this->findById($userId);
        
        if (!$user) {
            return false;
        }

        $user->assignRole($roleName);
        return true;
    }

    /**
     * Uklanja rolu korisniku
     *
     * @param int $userId
     * @param string $roleName
     * @return bool
     */
    public function removeRole(int $userId, string $roleName): bool
    {
        $user = $this->findById($userId);
        
        if (!$user) {
            return false;
        }

        $user->removeRole($roleName);
        return true;
    }

    /**
     * Pronalazi recentne korisnike
     *
     * @param int $limit
     * @return \Illuminate\Database\Eloquent\Collection
     */
    public function getRecentUsers(int $limit = 10)
    {
        return User::orderBy('created_at', 'desc')->limit($limit)->get();
    }
}
