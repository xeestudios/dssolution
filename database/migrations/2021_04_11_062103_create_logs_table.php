<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

class CreateLogsTable extends Migration
{
    /**
     * Run the migrations.
     *
     * @return void
     */
    public function up()
    {
        Schema::create('logs', function (Blueprint $table) {
            $table->increments('id');
            $table->string('event', 40);
            $table->string('controller', 40)->nullable();
            $table->string('method', 40)->nullable();
            $table->string('crud', 20)->nullable();
            $table->string('filename', 50)->nullable();
            $table->longText('url')->nullable();
            $table->longText('request')->nullable();
            $table->longText('response')->nullable();
            $table->integer('created_by')->nullable();
            $table->string('ip', 50)->nullable();
            $table->string('user_agent', 50)->nullable();
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
        Schema::dropIfExists('logs');
    }
}
