<?php

namespace Database\Seeders;

use App\Models\User;
use App\Models\Role;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;

class DatabaseSeeder extends Seeder
{
    /**
     * Seed-uje bazu podataka sa default ulogama i test korisnicima
     */
    public function run(): void
    {
        // Kreira default uloge
        $guestRole = Role::firstOrCreate(['name' => 'guest'], [
            'description' => 'Gost - može pregledati događaje bez registracije',
        ]);

        $userRole = Role::firstOrCreate(['name' => 'user'], [
            'description' => 'Registrovani korisnik - može kupovati karte',
        ]);

        $adminRole = Role::firstOrCreate(['name' => 'admin'], [
            'description' => 'Administrator - puni pristup sistemu',
        ]);

        // Test korisnički admin
        $adminUser = User::firstOrCreate(
            ['email' => 'admin@example.com'],
            [
                'name' => 'Admin',
                'password' => Hash::make('Admin123!'),
            ]
        );
        $adminUser->assignRole('admin');

        // Test korisnički obični korisnik
        $regularUser = User::firstOrCreate(
            ['email' => 'user@example.com'],
            [
                'name' => 'Regular User',
                'password' => Hash::make('User123!'),
            ]
        );
        $regularUser->assignRole('user');

        // Test korisnici za testiranje
        $testUsers = [
            [
                'name' => 'Aleksandra Vrzić',
                'email' => 'aleksandra@example.com',
                'password' => Hash::make('Aleksandra123!'),
                'role' => 'user',
            ],
            [
                'name' => 'Janja Vukelić',
                'email' => 'janja@example.com',
                'password' => Hash::make('Janja123!'),
                'role' => 'user',
            ],
            [
                'name' => 'Milica Drljača',
                'email' => 'milica@example.com',
                'password' => Hash::make('Milica123!'),
                'role' => 'user',
            ],
        ];

        foreach ($testUsers as $userData) {
            $role = $userData['role'];
            unset($userData['role']);

            $user = User::firstOrCreate(
                ['email' => $userData['email']],
                $userData
            );

            if ($role === 'user') {
                $user->assignRole('user');
            }
        }

        $this->command->info('✓ Uloge kreirane');
        $this->command->info('✓ Admin korisnik kreiran (admin@example.com / Admin123!)');
        $this->command->info('✓ Obični korisnik kreiran (user@example.com / User123!)');
        $this->command->info('✓ Test korisnici kreirani');
    }
}
