<?php

namespace App\Http\Controllers;

use App\Services\AuthenticationService;
use App\Services\PasswordResetService;
use App\Repositories\UserRepository;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Validation\ValidationException;

class AuthController extends Controller
{
    protected AuthenticationService $authService;
    protected PasswordResetService $passwordResetService;
    protected UserRepository $userRepository;

    public function __construct(
        AuthenticationService $authService,
        PasswordResetService $passwordResetService,
        UserRepository $userRepository
    ) {
        $this->authService = $authService;
        $this->passwordResetService = $passwordResetService;
        $this->userRepository = $userRepository;
    }

    /**
     * Registracija novog korisnika
     *
     * POST /api/auth/register
     */
    public function register(Request $request): JsonResponse
    {
        try {
            $result = $this->authService->register($request->all());

            return response()->json([
                'message' => $result['message'],
                'data' => $result['user'],
            ], 201);
        } catch (ValidationException $e) {
            return response()->json([
                'message' => 'Validacijska greška',
                'errors' => $e->errors(),
            ], 422);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri registraciji',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Login korisnika
     *
     * POST /api/auth/login
     */
    public function login(Request $request): JsonResponse
    {
        try {
            $result = $this->authService->login($request->all());

            return response()->json([
                'message' => $result['message'],
                'data' => [
                    'user' => $result['user'],
                    'token' => $result['token'],
                    'token_type' => $result['token_type'],
                    'expires_in' => $result['expires_in'],
                ],
            ], 200);
        } catch (ValidationException $e) {
            return response()->json([
                'message' => 'Validacijska greška',
                'errors' => $e->errors(),
            ], 422);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri prijavi',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Logout korisnika
     *
     * POST /api/auth/logout
     * Header: Authorization: Bearer {token}
     */
    public function logout(Request $request): JsonResponse
    {
        try {
            $result = $this->authService->logout($request->user());

            return response()->json($result, 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri odjavi',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Osvežava JWT token
     *
     * POST /api/auth/refresh
     * Header: Authorization: Bearer {token}
     */
    public function refreshToken(Request $request): JsonResponse
    {
        try {
            $result = $this->authService->refreshToken($request->user());

            return response()->json([
                'message' => $result['message'],
                'data' => [
                    'token' => $result['token'],
                    'token_type' => $result['token_type'],
                    'expires_in' => $result['expires_in'],
                ],
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri osvežavanju tokena',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Dobija profil prijavljivog korisnika
     *
     * GET /api/auth/me
     * Header: Authorization: Bearer {token}
     */
    public function me(Request $request): JsonResponse
    {
        try {
            $user = $request->user();

            return response()->json([
                'message' => 'Profil prijavljivog korisnika',
                'data' => $user,
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri preuzimanju profila',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Ažurira profil prijavljivog korisnika
     *
     * PUT /api/auth/profile
     * Header: Authorization: Bearer {token}
     */
    public function updateProfile(Request $request): JsonResponse
    {
        try {
            $user = $request->user();
            $data = $request->only(['name', 'email', 'password']);
            
            $updatedUser = $this->authService->updateProfile($user, array_filter($data));

            return response()->json([
                'message' => 'Profil uspešno ažuriran',
                'data' => $updatedUser,
            ], 200);
        } catch (ValidationException $e) {
            return response()->json([
                'message' => 'Validacijska greška',
                'errors' => $e->errors(),
            ], 422);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri ažuriranju profila',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * ✨ NOVO: Zahteva reset lozinke
     *
     * POST /api/auth/forgot-password
     * {
     *   "email": "korisnik@example.com"
     * }
     */
    public function forgotPassword(Request $request): JsonResponse
    {
        try {
            $request->validate([
                'email' => 'required|email',
            ]);

            $passwordReset = $this->passwordResetService->createResetToken($request->input('email'));

            // TODO: Pošalji email sa reset linknom
            // Mail::send('emails.reset-password', ['token' => $passwordReset->reset_token], ...);

            return response()->json([
                'message' => 'Reset link je poslat na vašu email adresu',
                'token' => $passwordReset->reset_token, // Za testiranje - OBRIŠI U PRODUKCIJI!
            ], 200);
        } catch (ValidationException $e) {
            return response()->json([
                'message' => 'Validacijska greška',
                'errors' => $e->errors(),
            ], 422);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri kreiranju reset tokena',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * ✨ NOVO: Resetuje lozinku
     *
     * POST /api/auth/reset-password
     * {
     *   "token": "reset_token_iz_maila",
     *   "password": "NovaLozinka123!",
     *   "password_confirmation": "NovaLozinka123!"
     * }
     */
    public function resetPassword(Request $request): JsonResponse
    {
        try {
            $request->validate([
             'token' => 'required|string',
            'password' => 'required|string|min:8|confirmed',
             ], [
             'password.min' => 'Lozinka mora da sadrži najmanje 8 karaktera.',
            'password.confirmed' => 'Lozinke se ne podudaraju.',
            'password.required' => 'Lozinka je obavezna.',
            ]);

            $user = $this->passwordResetService->resetPassword(
                $request->input('token'),
                $request->input('password')
            );

            return response()->json([
                'message' => 'Lozinka je uspešno resetovana',
                'data' => $user,
            ], 200);
        } catch (ValidationException $e) {
            return response()->json([
                'message' => 'Validacijska greška',
                'errors' => $e->errors(),
            ], 422);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri resetovanju lozinke',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * ✨ NOVO: Validira reset token
     *
     * POST /api/auth/validate-reset-token
     * {
     *   "token": "reset_token_iz_maila"
     * }
     */
    public function validateResetToken(Request $request): JsonResponse
    {
        try {
            $request->validate([
                'token' => 'required|string',
            ]);

            $passwordReset = $this->passwordResetService->validateResetToken($request->input('token'));

            return response()->json([
                'message' => 'Token je validan',
                'data' => [
                    'expires_at' => $passwordReset->expires_at,
                ],
            ], 200);
        } catch (ValidationException $e) {
            return response()->json([
                'message' => 'Nevaljani token',
                'errors' => $e->errors(),
            ], 422);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri validaciji tokena',
                'error' => $e->getMessage(),
            ], 500);
        }
    }
}
