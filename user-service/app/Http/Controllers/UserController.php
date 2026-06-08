<?php

namespace App\Http\Controllers;

use App\Repositories\UserRepository;
use Illuminate\Http\Request;
use Illuminate\Http\JsonResponse;
use Illuminate\Validation\ValidationException;

class UserController extends Controller
{
    protected UserRepository $userRepository;

    public function __construct(UserRepository $userRepository)
    {
        $this->userRepository = $userRepository;
        
        // Middleware koji provera da li je korisnik admin
        $this->middleware('auth:sanctum');
        $this->middleware('admin')->except(['show']);
    }

    /**
     * Lista svih korisnika (samo admin)
     *
     * GET /api/users?page=1&per_page=15
     */
    public function index(Request $request): JsonResponse
    {
        try {
            $perPage = $request->get('per_page', 15);
            $users = $this->userRepository->all($perPage);

            return response()->json([
                'message' => 'Lista korisnika',
                'data' => $users->items(),
                'pagination' => [
                    'total' => $users->total(),
                    'per_page' => $users->perPage(),
                    'current_page' => $users->currentPage(),
                    'total_pages' => $users->lastPage(),
                ],
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri preuzimanju liste korisnika',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Pretraga korisnika
     *
     * GET /api/users/search?q=aleksandra&per_page=15
     */
    public function search(Request $request): JsonResponse
    {
        try {
            $searchTerm = $request->get('q', '');
            $perPage = $request->get('per_page', 15);

            if (empty($searchTerm)) {
                return response()->json([
                    'message' => 'Pretraga zahteva minimalno 1 karakter',
                ], 400);
            }

            $users = $this->userRepository->search($searchTerm, $perPage);

            return response()->json([
                'message' => 'Rezultati pretrage',
                'data' => $users->items(),
                'pagination' => [
                    'total' => $users->total(),
                    'per_page' => $users->perPage(),
                    'current_page' => $users->currentPage(),
                    'total_pages' => $users->lastPage(),
                ],
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri pretrazi',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Pronalazi korisnika po ID-u
     *
     * GET /api/users/{id}
     */
    public function show(int $id): JsonResponse
    {
        try {
            $user = $this->userRepository->findById($id);

            if (!$user) {
                return response()->json([
                    'message' => 'Korisnik nije pronađen',
                ], 404);
            }

            return response()->json([
                'message' => 'Profil korisnika',
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
     * Ažurira korisnika (admin)
     *
     * PUT /api/users/{id}
     * {
     *   "name": "Novo Ime",
     *   "email": "novi@example.com"
     * }
     */
    public function update(Request $request, int $id): JsonResponse
    {
        try {
            $user = $this->userRepository->findById($id);

            if (!$user) {
                return response()->json([
                    'message' => 'Korisnik nije pronađen',
                ], 404);
            }

            $data = $request->only(['name', 'email', 'password']);

            // Proverava da li email već postoji
            if (isset($data['email']) && $this->userRepository->emailExists($data['email'], $id)) {
                return response()->json([
                    'message' => 'Email je već u upotrebi',
                ], 422);
            }

            // Ako se prosledi lozinka, heširuje je
            if (isset($data['password'])) {
                $data['password'] = bcrypt($data['password']);
            }

            $updatedUser = $this->userRepository->update($id, array_filter($data));

            return response()->json([
                'message' => 'Korisnik uspešno ažuriran',
                'data' => $updatedUser,
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri ažuriranju',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Briše korisnika (admin)
     *
     * DELETE /api/users/{id}
     */
    public function destroy(int $id): JsonResponse
    {
        try {
            $user = $this->userRepository->findById($id);

            if (!$user) {
                return response()->json([
                    'message' => 'Korisnik nije pronađen',
                ], 404);
            }

            // Sprečava brisanje sopstvenog naloga
            if ($user->id === auth()->user()->id) {
                return response()->json([
                    'message' => 'Ne možete obrisati sopstveni nalog',
                ], 403);
            }

            $this->userRepository->delete($id);

            return response()->json([
                'message' => 'Korisnik uspešno obrisan',
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri brisanju',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Pronalazi sve adminine
     *
     * GET /api/users/admins/list
     */
    public function getAdmins(): JsonResponse
    {
        try {
            $admins = $this->userRepository->getAdmins();

            return response()->json([
                'message' => 'Lista administatora',
                'data' => $admins,
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri preuzimanju liste administatora',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Pronalazi sve obične korisnike
     *
     * GET /api/users/regular/list
     */
    public function getRegularUsers(): JsonResponse
    {
        try {
            $users = $this->userRepository->getRegularUsers();

            return response()->json([
                'message' => 'Lista običnih korisnika',
                'data' => $users,
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri preuzimanju liste',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Dodeljuje rolu korisniku (admin)
     *
     * POST /api/users/{id}/assign-role
     * {
     *   "role": "admin"
     * }
     */
    public function assignRole(Request $request, int $id): JsonResponse
    {
        try {
            $request->validate([
                'role' => 'required|string',
            ]);

            $success = $this->userRepository->assignRole($id, $request->input('role'));

            if (!$success) {
                return response()->json([
                    'message' => 'Korisnik nije pronađen',
                ], 404);
            }

            return response()->json([
                'message' => 'Uloga uspešno dodeljena',
                'data' => $this->userRepository->getUserRoles($id),
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri dodeljivanju uloge',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Uklanja rolu korisniku (admin)
     *
     * DELETE /api/users/{id}/remove-role
     * {
     *   "role": "admin"
     * }
     */
    public function removeRole(Request $request, int $id): JsonResponse
    {
        try {
            $request->validate([
                'role' => 'required|string',
            ]);

            $success = $this->userRepository->removeRole($id, $request->input('role'));

            if (!$success) {
                return response()->json([
                    'message' => 'Korisnik nije pronađen',
                ], 404);
            }

            return response()->json([
                'message' => 'Uloga uspešno uklonjena',
                'data' => $this->userRepository->getUserRoles($id),
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri uklanjanju uloge',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Dobija sve uloge korisnika
     *
     * GET /api/users/{id}/roles
     */
    public function getRoles(int $id): JsonResponse
    {
        try {
            $roles = $this->userRepository->getUserRoles($id);

            return response()->json([
                'message' => 'Uloge korisnika',
                'data' => $roles,
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri preuzimanju uloga',
                'error' => $e->getMessage(),
            ], 500);
        }
    }

    /**
     * Broji sve korisnike
     *
     * GET /api/users/statistics/count
     */
    public function getStatistics(): JsonResponse
    {
        try {
            $totalUsers = $this->userRepository->count();
            $admins = count($this->userRepository->getAdmins());
            $regularUsers = count($this->userRepository->getRegularUsers());
            $recentUsers = $this->userRepository->getRecentUsers(5);

            return response()->json([
                'message' => 'Statistika korisnika',
                'data' => [
                    'total_users' => $totalUsers,
                    'admins' => $admins,
                    'regular_users' => $regularUsers,
                    'recent_users' => $recentUsers,
                ],
            ], 200);
        } catch (\Exception $e) {
            return response()->json([
                'message' => 'Greška pri preuzimanju statistike',
                'error' => $e->getMessage(),
            ], 500);
        }
    }
}
