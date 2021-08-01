<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\User;
use Illuminate\Database\QueryException as QE;
use Auth;

use Carbon\Carbon;
//This is for Batch Job
use Symfony\Component\Process\Exception\ProcessFailedException;
use Symfony\Component\Process\Process;

class ControlGroupSelectionController extends Controller{

    /**
     * Create a new controller instance.
     *
     * @return void
     */
    public function __construct()
    {
        $this->middleware('auth');
    }

    public function getFilesList(Request $request){
        
        $this->validate($request, [
            'file' => 'max:228192'
        ]);

        //$uploadedFile = $this->uploadFile($request);
        //$workingDir = '/Users/zeeshan/Sites/dssolution/public';  
        //$data['uploadedFile'] = $this->uploadFile($request);
        $data['workingDir'] = '/Users/zeeshan/Sites/dssolution/public';  
        $data['fileSource'] = $request['fileSource'];  
        $json = json_encode($data);
        
        $process = new Process(['python3', base_path().'/Scripts/cgs/cgs_getFilesList.py', $json]);
        $process->setTimeout(0);
        $process->run();

        if (!$process->isSuccessful()) {
            throw new ProcessFailedException($process);
        }
        
        echo $process->getOutput();

    }



    public function getVariables(Request $request){
        
        $data['username'] = 'zeeshan';
        $data['filename'] = $request['file'];  
        $json = json_encode($data);
        
        $process = new Process(['python3', base_path().'/Scripts/cgs/cgs_getVariables.py', $json]);
        $process->setTimeout(0);
        $process->run();

        if (!$process->isSuccessful()) {
            throw new ProcessFailedException($process);
        }
        
        echo $process->getOutput();

    }


    public function process(Request $request){
        
        $data['nb_groups'] = 'help';  
        $json = json_encode($data);
        
        $process = new Process(['python3', base_path().'/Scripts/cgs/cgs_main.py', $json]);
        $process->setTimeout(0);
        $process->run();

        if (!$process->isSuccessful()) {
            throw new ProcessFailedException($process);
        }
        
        echo $process->getOutput();

    }
    

    public function uploadFile($request){

        $filename = $request->file('file')->getClientOriginalName();
        $filename = Carbon::now()->timestamp.'-'.$filename;
        
        $destinationPath = base_path().'/public/uploads';
        $request->file('file')->move($destinationPath, $filename);

        return $destinationPath.'/'.$filename;
    }

    

    
}
