<?php

namespace App\Http\Controllers;

use Illuminate\Support\Facades\Hash;
use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Support\Str;
use Auth;
use DB;

class LoginController extends Controller
{
    /**
     * Create a new controller instance.
     *
     * @return void
     */
    public function __construct()
    {
        //
    }

    
    public function authenticate(Request $request){
        
        $this->validate($request, [
            'username' => 'required',
            'password' => 'required'
        ]);
            
        //$user = User::where('username', $request->input('username'))->first();

        $user = DB::table('users')
            ->join('roles', 'users.role_id', '=', 'roles.id')
            ->select('users.*', 'roles.permission_json')
            ->where('username',$request->input('username'))
            ->first();

        if($user){
            if(Hash::check($request->input('password'), $user->password)){
    
                $apikey = base64_encode(Str::random(40));
                User::where('username', $request->input('username'))->update(['api_key' => "$apikey"]);;
                unset($user->password);
                $user->permission_json = json_encode($user->permission_json); 
                $user->api_key = $apikey;
                return response()->json(['data' => $user, 'status' => 'success']);
    
            }else{
                return response()->json(['data'=> array('msg'=> 'Wrong Password'), 'status' => 'failed']);
            }
        }else{
            return response()->json(['data'=> array('msg'=> 'Wrong Credentials'), 'status' => 'failed']);
        }
    }

}
