<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Hash;
use Illuminate\Http\Request;
use Illuminate\Database\QueryException as QE;
use App\Models\User;
use Illuminate\Support\Str;
use Auth;

class UsersController extends Controller
{
    /**
     * Create a new controller instance.
     *
     * @return void
     */
    public function __construct()
    {
        //$this->middleware('auth');        
    }

    public function showAllUsers(){
        
        $user = Auth::user()->get();
        $data['data'] = User::select('id','username','first_name','last_name', 'email', 'phone', 'role_id')->get();
        //TODO
        $data['meta'] = array(
            "page" => 1,
            "pages" => 1,
            "perpage" => 10,
            "total" => 20,
            "sort" => "asc",
            "field" => "id"
        );
        return response()->json($data);

    }

    public function showOneUser($id){

        $data = User::select('id','username','first_name','last_name', 'email', 'phone', 'role_id')->where('id', $id)->first();
        return response()->json($data, 200);
        
    }

    public function validateUsername(Request $request){
        
        $result = User::select('id')->where('username', $request->username)->count() > 0 ? false : true;
        
        return response()->json($result, 200);
    }

    public function create(Request $request){

        $this->validate($request, [
            'username' => 'required|unique:users,username',
            'email' => 'required|unique:users',
            'phone' => 'required|unique:users',
        ]);
        $data = User::create($request->all());
        return response()->json(['msg' => 'Successfully Created', 'status' => 'success'], 201);

    }

    public function delete($id){

        //User::findOrFail($id)->delete();
        $user = User::findOrFail($id);
        $user->update(['is_delete' => 1]);

        return response()->json(['status' => 'success'], 200);
    }

    public function update(Request $request){
        
        $this->validate($request, [
            'username' => 'required|unique:users,username,'.$request->id,
            'email' => 'required|unique:users,email,'.$request->id,
            'phone' => 'required|unique:users,phone,'.$request->id
        ]);

        $user = User::findOrFail($request->id);
        $user->update($request->all());
        return response()->json(['msg' => 'Successfully Updated', 'status' => 'success'], 200);
    
    }

    public function changePassword(Request $request){

        $user = User::findOrFail($request->id);
        $request->password = Hash::make($request->input('password'));
        $user->update(['password'=> $request->password]);

        return response()->json(['msg' => 'Successfully Updated', 'status' => 'success'], 200);
    }

}
