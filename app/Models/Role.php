<?php 

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Role extends Model{


    /**
     * The attributes that are mass assignable.
     *
     * @var array
     */
    protected $fillable = [
        'name','role_level','permission_json','is_active','is_delete'
    ];

    /**
     * The attributes excluded from the model's JSON form.
     *
     * @var array
     */
    protected $hidden = [];
    
}

