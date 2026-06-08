<?php

use Illuminate\Support\Facades\Route;
use App\Http\Controllers\AuthController;
use App\Http\Controllers\UserController;

/*
|--------------------------------------------------------------------------
| API Routes za User Microservice
|--------------------------------------------------------------------------
|
| Sve rute su prefixovane sa /api
| API Gateway rutira zahteve ka ovom servisu
|
*/

Route::prefix('auth')->group(function () {
    // ========== JAVNE RUTE (bez autentifikacije) ==========
    
    Route::post('register', [AuthController::class, 'register'])->name('register');
    Route::post('login', [AuthController::class, 'login'])->name('login');
    
    // ✨ NOVE: Password Reset rute (javne)
    Route::post('forgot-password', [AuthController::class, 'forgotPassword'])->name('forgot-password');
    Route::post('reset-password', [AuthController::class, 'resetPassword'])->name('reset-password');
    Route::post('validate-reset-token', [AuthController::class, 'validateResetToken'])->name('validate-reset-token');

    // ========== ZAŠTIĆENE RUTE (sa autentifikacijom) ==========
    
    Route::middleware('auth:sanctum')->group(function () {
        Route::post('logout', [AuthController::class, 'logout'])->name('logout');
        Route::post('refresh', [AuthController::class, 'refreshToken'])->name('refresh-token');
        Route::get('me', [AuthController::class, 'me'])->name('me');
        Route::put('profile', [AuthController::class, 'updateProfile'])->name('update-profile');
    });
});

// ========== RUTE ZA UPRAVLJANJE KORISNICIMA ==========

Route::middleware('auth:sanctum')->group(function () {
    
    // Pregled profila (svako može pregledati bilo koji profil)
    Route::get('users/{id}', [UserController::class, 'show'])->name('users.show');
    
    // Admin rute
    Route::middleware('admin')->group(function () {
        // CRUD operacije
        Route::get('users', [UserController::class, 'index'])->name('users.index');
        Route::get('users/search', [UserController::class, 'search'])->name('users.search');
        Route::put('users/{id}', [UserController::class, 'update'])->name('users.update');
        Route::delete('users/{id}', [UserController::class, 'destroy'])->name('users.destroy');
        
        // Uloge
        Route::post('users/{id}/assign-role', [UserController::class, 'assignRole'])->name('users.assign-role');
        Route::delete('users/{id}/remove-role', [UserController::class, 'removeRole'])->name('users.remove-role');
        Route::get('users/{id}/roles', [UserController::class, 'getRoles'])->name('users.get-roles');
        
        // Filtriranje po ulogama
        Route::get('users/admins/list', [UserController::class, 'getAdmins'])->name('users.admins');
        Route::get('users/regular/list', [UserController::class, 'getRegularUsers'])->name('users.regular');
        
        // Statistika
        Route::get('users/statistics/count', [UserController::class, 'getStatistics'])->name('users.statistics');
    });
});

// ========== HEALTH CHECK ==========

Route::get('health', function () {
    return response()->json([
        'status' => 'ok',
        'service' => 'user-microservice',
        'timestamp' => now(),
    ]);
})->name('health');
