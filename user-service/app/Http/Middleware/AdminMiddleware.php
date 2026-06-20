<?php

namespace App\Http\Middleware;

use Closure;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;

class AdminMiddleware
{
    /**
     * Proverava da li je korisnik admin
     *
     * @param  \Illuminate\Http\Request  $request
     * @param  \Closure  $next
     * @return mixed
     */
    public function handle(Request $request, Closure $next)
    {
        // Proverava da li je korisnik uopšte ulogovan
        if (!$request->user()) {
            return response()->json([
                'message' => 'Neovlašćen pristup',
            ], 401);
        }

        // Proverava da li ima 'admin' rolu
        if (!$request->user()->hasRole('admin')) {
            return response()->json([
                'message' => 'Zabranjen pristup - potrebna admin uloga',
            ], 403);
        }

        return $next($request);
    }
}
