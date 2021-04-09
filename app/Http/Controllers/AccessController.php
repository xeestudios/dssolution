<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Access;
use Auth;

class AccessController extends Controller{

    /**
     * Create a new controller instance.
     *
     * @return void
     */
    public function __construct()
    {
        $this->middleware('auth');
    }

    public function showAllAccess(){

        $data = Access::select('controller','action','name','group','type')->get();
        return response()->json(['data' => $data, 'status'=> 200]);

    }

    public function showOneAccess($id){

        $data = Access::select('id','controller','action','name','group','type')->where(['id'=> $id])->get();
        return response()->json(['data' => $data, 'status' => 200]);
        
    }
    
    public function create(Request $request){
        
        $request['permission_json'] = json_encode($request->permission_json);
        $data = Access::create($request->all());
        return response()->json(['data' => $data, 'status' => 201]);

    }

    public function delete($id){

        Access::findOrFail($id)->delete();

        return response()->json('Deleted Successfully', 200);
    }

    public function update(Request $request){

        $role = Access::findOrFail($request->id);
        $role->update($request->all());

        return response()->json(['data' => $role, 'status' => 200]);
    }

    
}
