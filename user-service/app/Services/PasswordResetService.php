<?php

namespace App\Services;

use App\Models\User;
use App\Models\PasswordReset;
use Illuminate\Support\Str;
use Illuminate\Support\Facades\Hash;
use Illuminate\Validation\ValidationException;

class PasswordResetService
{
    /**
     * Generiše reset token i kreira PasswordReset zapis
     *
     * @param string $email
     * @return PasswordReset|null
     * @throws ValidationException
     */
    public function createResetToken(string $email): ?PasswordReset
    {
        // Pronalazi korisnika po email-u
        $user = User::where('email', $email)->first();

        if (!$user) {
            throw ValidationException::withMessages([
                'email' => ['Korisnik sa ovom email adresom ne postoji.'],
            ]);
        }

        // Briše sve stare reset tokene
        $user->passwordResets()->delete();

        // Generiše novi reset token
        $resetToken = Str::random(60);

        // Kreira novi PasswordReset zapis (važi 1 sat)
        $passwordReset = $user->passwordResets()->create([
            'reset_token' => $resetToken,
            'expires_at' => now()->addHour(),
        ]);

        return $passwordReset;
    }

    /**
     * Pronalazi validan reset token
     *
     * @param string $token
     * @return PasswordReset|null
     * @throws ValidationException
     */
    public function validateResetToken(string $token): ?PasswordReset
    {
        $passwordReset = PasswordReset::where('reset_token', $token)->first();

        if (!$passwordReset) {
            throw ValidationException::withMessages([
                'token' => ['Nevaljani reset token.'],
            ]);
        }

        // Proverava da li je token validan (nije korišćen i nije istekao)
        if (!$passwordReset->isValid()) {
            throw ValidationException::withMessages([
                'token' => ['Reset token je istekao ili već korišćen. Zahtevajte novi.'],
            ]);
        }

        return $passwordReset;
    }

    /**
     * Resetuje lozinku korisnika
     *
     * @param string $token
     * @param string $newPassword
     * @return User
     * @throws ValidationException
     */
    public function resetPassword(string $token, string $newPassword): User
    {
        // Validira reset token
        $passwordReset = $this->validateResetToken($token);

        // Pronalazi korisnika
        $user = $passwordReset->user;

        // Validira novu lozinku
        if (strlen($newPassword) < 8) {
            throw ValidationException::withMessages([
                'password' => ['Lozinka mora da sadrži najmanje 8 karaktera.'],
            ]);
        }

        // Ažurira lozinku
        $user->update(['password' => Hash::make($newPassword)]);

        // Označava token kao korišćen
        $passwordReset->markAsUsed();

        // Briše sve ostale tokene za sigurnost
        $user->passwordResets()->where('id', '!=', $passwordReset->id)->delete();

        return $user;
    }

    /**
     * Briše sve istekle reset tokene (cleanup)
     * Trebalo bi pokrenuti kao scheduled task
     */
    public function deleteExpiredTokens(): void
    {
        PasswordReset::where('expires_at', '<', now())->delete();
    }
}
