<?php

namespace Tests\Feature;

use App\Models\User;
use App\Models\PasswordReset;
use Illuminate\Foundation\Testing\RefreshDatabase;
use Tests\TestCase;

class AuthenticationTest extends TestCase
{
    use RefreshDatabase;

    /**
     * Test: Uspešna registracija
     */
    public function test_user_can_register(): void
    {
        $response = $this->postJson('/api/auth/register', [
            'name' => 'Test User',
            'email' => 'test@example.com',
            'password' => 'Password123!',
            'password_confirmation' => 'Password123!',
        ]);

        $response->assertStatus(201)
                 ->assertJsonPath('message', 'Korisnik uspešno registrovan')
                 ->assertJsonPath('data.email', 'test@example.com');

        $this->assertDatabaseHas('users', [
            'email' => 'test@example.com',
        ]);
    }

    /**
     * Test: Registracija sa već postojećim email-om
     */
    public function test_user_cannot_register_with_existing_email(): void
    {
        User::factory()->create([
            'email' => 'test@example.com',
        ]);

        $response = $this->postJson('/api/auth/register', [
            'name' => 'Another User',
            'email' => 'test@example.com',
            'password' => 'Password123!',
            'password_confirmation' => 'Password123!',
        ]);

        $response->assertStatus(422)
                 ->assertJsonPath('errors.email.0', 'Email adresa je već registrovana.');
    }

    /**
     * Test: Uspešan login
     */
    public function test_user_can_login(): void
    {
        $user = User::factory()->create([
            'email' => 'test@example.com',
            'password' => bcrypt('Password123!'),
        ]);

        $response = $this->postJson('/api/auth/login', [
            'email' => 'test@example.com',
            'password' => 'Password123!',
        ]);

        $response->assertStatus(200)
                 ->assertJsonPath('message', 'Uspešna prijava')
                 ->assertJsonPath('data.user.email', 'test@example.com')
                 ->assertJsonStructure([
                     'data' => [
                         'token',
                         'token_type',
                         'expires_in',
                     ]
                 ]);
    }

    /**
     * Test: Logout
     */
    public function test_user_can_logout(): void
    {
        $user = User::factory()->create();
        $token = $user->createToken('test-token')->plainTextToken;

        $response = $this->withHeader('Authorization', "Bearer $token")
                        ->postJson('/api/auth/logout');

        $response->assertStatus(200)
                 ->assertJsonPath('message', 'Uspešna odjava');

        $this->assertDatabaseEmpty('personal_access_tokens');
    }

    /**
     * ✨ TEST: Zahteva password reset
     */
    public function test_user_can_request_password_reset(): void
    {
        $user = User::factory()->create([
            'email' => 'test@example.com',
        ]);

        $response = $this->postJson('/api/auth/forgot-password', [
            'email' => 'test@example.com',
        ]);

        $response->assertStatus(200)
                 ->assertJsonPath('message', 'Reset link je poslat na vašu email adresu')
                 ->assertJsonStructure([
                     'token',
                 ]);

        // Proverava da je kreirat password reset u bazi
        $this->assertDatabaseHas('password_resets', [
            'user_id' => $user->id,
        ]);
    }

    /**
     * ✨ TEST: Validira reset token
     */
    public function test_can_validate_reset_token(): void
    {
        $user = User::factory()->create();
        $passwordReset = $user->passwordResets()->create([
            'reset_token' => 'valid-token-123',
            'expires_at' => now()->addHour(),
        ]);

        $response = $this->postJson('/api/auth/validate-reset-token', [
            'token' => 'valid-token-123',
        ]);

        $response->assertStatus(200)
                 ->assertJsonPath('message', 'Token je validan');
    }

    /**
     * ✨ TEST: Odbija istekao reset token
     */
    public function test_cannot_validate_expired_reset_token(): void
    {
        $user = User::factory()->create();
        $passwordReset = $user->passwordResets()->create([
            'reset_token' => 'expired-token-123',
            'expires_at' => now()->subHour(), // Istekao je
        ]);

        $response = $this->postJson('/api/auth/validate-reset-token', [
            'token' => 'expired-token-123',
        ]);

        $response->assertStatus(422)
                 ->assertJsonPath('errors.token.0', 'Reset token je istekao ili već korišćen. Zahtevajte novi.');
    }

    /**
     * ✨ TEST: Resetuje lozinku
     */
    public function test_user_can_reset_password(): void
    {
        $user = User::factory()->create([
            'password' => bcrypt('OldPassword123!'),
        ]);

        $passwordReset = $user->passwordResets()->create([
            'reset_token' => 'valid-reset-token',
            'expires_at' => now()->addHour(),
        ]);

        $response = $this->postJson('/api/auth/reset-password', [
            'token' => 'valid-reset-token',
            'password' => 'NewPassword123!',
            'password_confirmation' => 'NewPassword123!',
        ]);

        $response->assertStatus(200)
                 ->assertJsonPath('message', 'Lozinka je uspešno resetovana');

        // Proverava da je token označen kao korišćen
        $this->assertNotNull($passwordReset->refresh()->used_at);

        // Proverava da je lozinka promenjena
        $user->refresh();
        $this->assertTrue(\Hash::check('NewPassword123!', $user->password));
    }

    /**
     * ✨ TEST: Odbija reset sa pogrešnom lozinkom
     */
    public function test_cannot_reset_password_with_weak_password(): void
    {
        $user = User::factory()->create();
        $passwordReset = $user->passwordResets()->create([
            'reset_token' => 'valid-reset-token',
            'expires_at' => now()->addHour(),
        ]);

        $response = $this->postJson('/api/auth/reset-password', [
            'token' => 'valid-reset-token',
            'password' => 'weak',
            'password_confirmation' => 'weak',
        ]);

        $response->assertStatus(422)
                 ->assertJsonPath('errors.password.0', 'Lozinka mora da sadrži najmanje 8 karaktera.');
    }

    /**
     * Test: Pristup bez tokena vraća 401
     */
    public function test_unauthenticated_user_cannot_access_protected_routes(): void
    {
        $response = $this->getJson('/api/auth/me');

        $response->assertStatus(401);
    }
}
