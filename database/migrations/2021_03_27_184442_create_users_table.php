<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateUsersTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('users', function (Blueprint $table) {
            $table->increments('id');
            $table->string('username', 30)->unique();
            $table->string('first_name', 20)->nullable();
            $table->string('last_name', 20)->nullable();
            $table->string('email', 100)->unique();
            $table->string('phone', 20)->nullable()->unique();
            $table->string('password')->nullable();
            $table->string('api_key', 100)->nullable();
            $table->integer('role_id')->nullable();
            $table->string('role_type', 20)->nullable();
            $table->timestamp('change_password_on')->nullable();
            $table->string('avatar', 100)->nullable();
            $table->string('timezone', 20)->nullable()->default('Asia/Dubai');
            $table->timestamp('last_login')->nullable();
            $table->string('last_login_ip', 30)->nullable();
            $table->tinyInteger('is_super_admin')->nullable()->default(0);
            $table->tinyInteger('is_active')->nullable()->default(1);
            $table->tinyInteger('is_delete')->nullable()->default(0);
            $table->integer('created_by')->nullable();
            $table->integer('updated_by')->nullable();
            $table->timestamps();
        });
    }

    /**
     * Reverse the migrations.
     *
     * @return void
     */
    public function down()
    {
        Schema::dropIfExists('users');
    }
}
