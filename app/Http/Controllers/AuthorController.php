<?php

namespace App\Http\Controllers;

use App\Models\Author;
use Illuminate\Http\Request;
use Auth;

class AuthorController extends Controller{

    /**
     * Create a new controller instance.
     *
     * @return void
     */
    public function __construct()
    {
        //$this->middleware('auth');
    }

    public function showAllAuthors(){
        
        $user = Auth::user()->get();
        return response()->json(['data' => Author::all(), 'user'=> $user[0]->id]);

    }

    public function showOneAuthor($id){

        return response()->json(Author::find($id));
        
    }

    public function create(Request $request){


        $this->validate($request, [
            'name' => 'required',
            'email' => 'required|email|unique:authors',
            'location' => 'required|alpha'
        ]);
        
        $author = Author::create($request->all());

        
        return response()->json($author, 201);

    }

    public function update($id, Request $request){

        $author = Author::findOrFail($id);
        $author->update($request->all());

        return response()->json($author, 200);

    }

    public function delete($id){

        Author::findOrFail($id)->delete();

        return response()->json('Deleted Successfully', 200);
    }
}