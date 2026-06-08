<?php

namespace App\Services;

use App\Models\User;
use App\Models\Role;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;

class AuthenticationService
{
    /**
     * Registruje novog korisnika
     *
     * @param array $credentials
     * @return array
     * @throws ValidationException
     */
    public function register(array $credentials): array
    {
        // Validacija kredencijala
        $this->validateRegistration($credentials);

        // Proverava da li email već postoji
        if (User::where('email', $credentials['email'])->exists()) {
            throw ValidationException::withMessages([
                'email' => ['Email adresa je već registrovana.'],
            ]);
        }

        // Kreira novog korisnika
        $user = User::create([
            'name' => $credentials['name'],
            'email' => $credentials['email'],
            'password' => Hash::make($credentials['password']),
        ]);

        // Dodeljuje default 'user' rolu
        $user->assignRole('user');

        return [
            'message' => 'Korisnik uspešno registrovan',
            'user' => $user,
        ];
    }

    /**
     * Prijavljuje korisnika i generiše token
     *
     * @param array $credentials
     * @return array
     * @throws ValidationException
     */
    public function login(array $credentials): array
    {
        // Validacija kredencijala
        $this->validateLogin($credentials);

        // Pronalazi korisnika po email-u
        $user = User::where('email', $credentials['email'])->first();

        // Ako korisnik ne postoji ili lozinka nije tačna
        if (!$user || !Hash::check($credentials['password'], $user->password)) {
            throw ValidationException::withMessages([
                'email' => ['Kredencijali nisu validni.'],
            ]);
        }

        // Generiše Sanctum token
        $token = $user->createToken('api_token', ['*'], now()->addHours(8))->plainTextToken;

        return [
            'message' => 'Uspešna prijava',
            'user' => $user,
            'token' => $token,
            'token_type' => 'Bearer',
            'expires_in' => 8 * 3600, // 8 sati u sekundama
        ];
    }

    /**
     * Odjavljuje korisnika
     *
     * @param User $user
     * @return array
     */
    public function logout(User $user): array
    {
        // Briše sve tokene korisnika
        $user->tokens()->delete();

        return [
            'message' => 'Uspešna odjava',
        ];
    }

    /**
     * Osvežava token
     *
     * @param User $user
     * @return array
     */
    public function refreshToken(User $user): array
    {
        // Briše stari token
        $user->currentAccessToken()->delete();

        // Generiše novi token
        $token = $user->createToken('api_token', ['*'], now()->addHours(8))->plainTextToken;

        return [
            'message' => 'Token uspešno osvežen',
            'token' => $token,
            'token_type' => 'Bearer',
            'expires_in' => 8 * 3600,
        ];
    }

    /**
     * Pronalazi korisnika po ID-u
     *
     * @param int $userId
     * @return User|null
     */
    public function getUserById(int $userId): ?User
    {
        return User::find($userId);
    }

    /**
     * Ažurira profil korisnika
     *
     * @param User $user
     * @param array $data
     * @return User
     * @throws ValidationException
     */
    public function updateProfile(User $user, array $data): User
    {
        // Ako menja email, proveri da li je već zauzet
        if (isset($data['email']) && $data['email'] !== $user->email) {
            if (User::where('email', $data['email'])->exists()) {
                throw ValidationException::withMessages([
                    'email' => ['Email adresa je već u upotrebi.'],
                ]);
            }
        }

        // Ako menja lozinku
        if (isset($data['password'])) {
            $data['password'] = Hash::make($data['password']);
        }

        $user->update($data);

        return $user;
    }

    /**
     * Validira registracijske kredencijale
     *
     * @param array $credentials
     * @throws ValidationException
     */
    private function validateRegistration(array $credentials): void
    {
        $errors = [];

        if (empty($credentials['name'])) {
            $errors['name'] = ['Ime je obavezno.'];
        }

        if (empty($credentials['email']) || !filter_var($credentials['email'], FILTER_VALIDATE_EMAIL)) {
            $errors['email'] = ['Unesite validnu email adresu.'];
        }

        if (empty($credentials['password']) || strlen($credentials['password']) < 8) {
            $errors['password'] = ['Lozinka mora da sadrži najmanje 8 karaktera.'];
        }

        if (($credentials['password'] ?? null) !== ($credentials['password_confirmation'] ?? null)) {
            $errors['password'] = ['Lozinke se ne poklapaju.'];
        }

        if (!empty($errors)) {
            throw ValidationException::withMessages($errors);
        }
    }

    /**
     * Validira login kredencijale
     *
     * @param array $credentials
     * @throws ValidationException
     */
    private function validateLogin(array $credentials): void
    {
        $errors = [];

        if (empty($credentials['email'])) {
            $errors['email'] = ['Email je obavezan.'];
        }

        if (empty($credentials['password'])) {
            $errors['password'] = ['Lozinka je obavezna.'];
        }

        if (!empty($errors)) {
            throw ValidationException::withMessages($errors);
        }
    }
}
