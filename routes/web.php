<?php

/** @var \Laravel\Lumen\Routing\Router $router */

/*
|--------------------------------------------------------------------------
| Application Routes
|--------------------------------------------------------------------------
|
| Here is where you can register all of the routes for an application.
| It is a breeze. Simply tell Lumen the URIs it should respond to
| and give it the Closure to call when that URI is requested.
|
 */

$router->get('/', function () use ($router) {
    return $router->app->version();
});

$router->group(['prefix' => 'api'], function () use ($router) {

    $router->post('login','LoginController@authenticate');

    /******* Users *********** */
    $router->post('dummy', ['uses' => 'UsersController@dummy']);
    $router->get('users', ['uses' => 'UsersController@showAllUsers']);
    $router->get('users/{id}', ['uses' => 'UsersController@showOneUser']);
    $router->post('users', ['uses' => 'UsersController@create']);
    $router->post('updateUser', ['uses' => 'UsersController@update']);
    $router->post('changePassword', ['uses' => 'UsersController@changePassword']);
    $router->delete('users/{id}', ['uses' => 'UsersController@delete']);
    $router->post('validateUsername', ['uses' => 'UsersController@validateUsername']);

    /******* Roles *********** */
    $router->get('roles', ['uses' => 'RolesController@showAllRoles']);
    $router->get('roles/{id}', ['uses' => 'RolesController@showOneRole']);
    $router->post('roles', ['uses' => 'RolesController@create']);
    $router->post('updateRole', ['uses' => 'RolesController@update']);
    $router->delete('roles/{id}', ['uses' => 'RolesController@delete']);
    
    /******* Access *********** */
    $router->get('access', ['uses' => 'AccessController@showAllAccess']);
    
    
    /******* Dummy *********** */
    $router->get('authors', ['uses' => 'AuthorController@showAllAuthors']);
    $router->get('authors/{id}', ['uses' => 'AuthorController@showOneAuthor']);
    $router->post('authors', ['uses' => 'AuthorController@create']);
    $router->delete('authors/{id}', ['uses' => 'AuthorController@delete']);
    $router->put('authors/{id}', ['uses' => 'AuthorController@update']);
    
});
