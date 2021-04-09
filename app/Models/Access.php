<?php 

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Access extends Model{

    public $table = "access";
    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'controller', 'action','name', 'group','type'
    ];

    /**
     * The attributes excluded from the model's JSON form.
     *
     * @var array
     */
    protected $hidden = [];
    
}

