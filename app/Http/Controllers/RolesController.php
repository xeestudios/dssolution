<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Models\Role;
use App\Models\User;
use Illuminate\Database\QueryException as QE;
use Auth;

class RolesController extends Controller{

    /**
     * Create a new controller instance.
     *
     * @return void
     */
    public function __construct()
    {
        $this->middleware('auth');
    }

    public function showAllRoles(){

        $data = Role::select('id','name','role_level')->get();
        return response()->json(['data' => $data, 'status'=> 200]);

    }

    public function showOneRole($id){

        $data = Role::select('id','name','role_level','permission_json', 'is_active')->where(['id'=> $id, 'is_active' => '1'])->get();
        return response()->json(['data' => $data, 'status' => 200]);
        
    }
    
    public function create(Request $request){
        
        
        $this->validate($request, [
            'name' => 'required|unique:roles,name'
        ]);

        $data = Role::create($request->all());
        return response()->json(['msg' => 'Successfully Created', 'status' => 201]);

    }

    public function delete($id){
        
        $role = Role::findOrFail($id);
        $role->update(['is_active' => 0, 'is_delete' => 1]);

        //Remove roles from all users which were using this role.
        $users = User::where("role_id", $id)->update(array('role_id' => Null));

        return response()->json(['data' => 'Deleted Successfully', 'status' => 200]);
    }

    public function update(Request $request){

        $this->validate($request, [
            'name' => 'required|unique:roles,name,'.$request->id
        ]);

        $role = Role::findOrFail($request->id);
        $role->update($request->all());

        return response()->json(['msg' => 'Successfully Updated', 'status' => 200]);
    }

    //
    /*
    public function executeNewRoles(sfWebRequest $request) {



        $user_id = $this->getUser()->getAttribute("user_id");
        $user = sfGuardUserTable::getInstance()->findOneBy("id", $user_id);
        $user instanceof sfGuardUser;
        if ($this->getUser()->getAttribute('role') == 'ADMIN') {
            $possible_views = PossibleViewsTable::getInstance()->findAll();
        } else {
            $custom_role = $user->getCustomRoleId();
            if (!is_null($custom_role)) {
                $current_role = RolePermissionsTable::getInstance()->findOneBy("id", $custom_role);
                $current_role instanceof RolePermissions;
                $permissions = json_decode($current_role->getPermissionsJson());
                $alll_priv = PossibleViewsTable::getInstance()->findAll();
                $tmp_rpiv = array();
                foreach ($alll_priv as $ap) {
                    if (!isset($tmp_rpiv[$ap['model']])) {
                        $tmp_rpiv[$ap['model']] = array();
                    }
                    $tmp_rpiv[$ap['model']][] = $ap['model'] . "_" . $ap['action'];
                }
                $p_permis = array();
                foreach ($permissions as $name => $per) {

                    if (isset($tmp_rpiv[$name])) {
                        $tmp_peermi = PossibleViewsTable::getInstance()->findBySql("model = '$name' ");
                        foreach ($tmp_peermi as $pp) {
                            $p_permis[] = $pp;
                        }e
                    } else {
                        $nam_t = explode("_", $name);
                        $tmp_peermi = PossibleViewsTable::getInstance()->findBySql("model = '{$nam_t[0]}' AND action = '{$nam_t[1]}'  ");
                        if (count($tmp_peermi))
                            $p_permis[] = $tmp_peermi[0];
                        //try to find one permision
                    }
                }

                $possible_views = $p_permis;
            } else {
                $possible_views = PossibleViewsTable::getInstance()->findAll();
            }
        }

        $possible_clients = $this->getUser()->getAttribute("possible_clients");
        $cid = $request->getParameter("cid", null);

        if (is_null($cid)) {
            $cid = sfContext::getInstance()->getUser()->getClientId();
            if (!is_null($possible_clients) && $possible_clients != '') {
                $tmp_c = explode(",", $possible_clients);
                $cid = $tmp_c[0];
                $roles = RolePermissionsTable::getInstance()->findBySql(" client_id IN ($possible_clients) ");
            } else {

                $roles = RolePermissionsTable::getInstance()->findBySql(" client_id  = $cid  ");
            }
        } else {
            $roles = RolePermissionsTable::getInstance()->findBySql(" client_id  = $cid ");
        }

        $this->roles = $roles;


        // $roles_users = array();
        // foreach ($roles as $rola) {
        //     if (!isset($roles_users[$rola['id']])) {
        //         $roles_users[$rola['id']] = 0;
        //     }
        //     $total_users = sfGuardUserTable::getInstance()->findBySql("is_active = 1 AND custom_role_id = {$rola['id']} ");
        //     $roles_users[$rola['id']] = count($total_users);
        // }

        // $this->roles_users = $roles_users;


        $main_views = array();
        $i = 10000;
        $all_viows = array();


        foreach ($possible_views as $ps_v) {
            if (!isset($main_views[$ps_v['display_group']])) {
                $main_views[$ps_v['display_group']] = $ps_v['display_group'];

                $tmp = array();
                $tmp['index'] = $ps_v['display_group'];
                $tmp['id'] = $ps_v['display_group'];
                $tmp['model'] = $ps_v['display_group'];
                $tmp['display_group'] = $ps_v['display_group'];
                $tmp['parent'] = 0;
                $tmp['action'] = "";
                $tmp['name'] = "";
                $all_viows[] = $tmp;
                $i++;
            }
            $tmp2 = array();
            $tmp2['index'] = $ps_v['id'];
            $tmp2['id'] = $ps_v['model'] . "_" . $ps_v['action'];
            $tmp2['model'] = $ps_v['display_group'];
            $tmp2['parent'] = $main_views[$ps_v['display_group']];
            $tmp2['action'] = $ps_v['action'];
            $tmp2['name'] = $ps_v['name'];
            $all_viows[] = $tmp2;
        }
        $this->possible_views = $all_viows;

        $c_a = array();
        if ($this->getUser()->getAttribute('role') == 'ADMIN') {
            $cid = $request->getParameter("cid", 1);
            $possible_clients = $this->getUser()->getAttribute("possible_clients");
            if (!is_null($possible_clients) && $possible_clients != '') {
                $this->clients = $clients = ClientTable::getInstance()->findBySql("is_active = 1 AND id IN($possible_clients) ");
            } else {
                $this->clients = $clients = ClientTable::getInstance()->findBySql("is_active = 1 ");
            }
            $c_a[0] = "All";
        } else {
            $cid = sfContext::getInstance()->getUser()->getClientId();
            $this->clients = $clients = ClientTable::getInstance()->findBySql("id = $cid");
            $c_a[0] = $clients[0]['name'];
        }

        foreach ($clients as $c) {
            $c_a[$c['id']] = $c['name'];
        }
        $this->c_a = $c_a;
        $this->client_id = $cid;
    }

    public function executeNewSaveRole(sfWebRequest $request) {
        $selected_role = $request->getParameter("selected_role");
        $name = $request->getParameter('name');
        $customer = $request->getParameter('customer_id');
        $role_level = $request->getParameter("role_level", 0);
        $is_active = $request->getParameter('is_active');


        //save info that user update/save role

        $permissions = array();

        $permissions = $request->getPostParameters();


        unset($permissions['role_level']);
        unset($permissions['customer_id']);
        unset($permissions['is_active']);
        unset($permissions['selected_role']);
        unset($permissions['name']);

        $user_id = $this->getUser()->getAttribute("user_id");
        $permissions2 = $permissions;

        if (count($permissions2) == 0) {
            echo json_encode(['error' => 'You have not selected any permissions']);
            return sfView::NONE;
        }

        foreach ($permissions2 as $per_name => $value) {
            $correct_name = str_replace("_", " ", $per_name);

            $possible_v = PossibleViewsTable::getInstance()->findBySql("display_group = '$correct_name'");
            if (count($possible_v) > 0) {
                unset($permissions[$per_name]);
                foreach ($possible_v as $pp) {
                    $permissions[$pp['model'] . "_" . $pp['action']] = $value;
                }
            }
        }


        if (is_null($selected_role) || $selected_role == '') {
            $role = new RolePermissions();
        } else {
            $role = RolePermissionsTable::getInstance()->findOneBy("id", $selected_role);
            $now = gmdate("Y-m-d H:i:s");
            $log = new AdminLog();
            $log->setClientName($selected_role);
            $log->setExtraInfo('UPDATE of role by ' . $user_id);
            $log->setRodzaj('INFO');
            $log->setStatusName($role['name']);
            $log->setCreatedAt($now);
            $log->setAddTimeGm($now);
            $log->save();
        }
        if (is_null($customer) || $customer == '') {
            $customer = 0;
        }
        if ($is_active == 'true' || $is_active == 1) {
            $role->setIsActive(1);
        } else {
            $role->setIsActive(0);
        }


        $role->setRoleLevel($role_level);
        $role->setClientId($customer);
        $role->setName($name);
        $role->setPermissionsJson(json_encode($permissions));
        $role->save();
        if (is_null($selected_role) || $selected_role == '') {
            $now = gmdate("Y-m-d H:i:s");
            $log = new AdminLog();
            $log->setClientName($role->getId());
            $log->setExtraInfo('UPDATE of role by ' . $user_id);
            $log->setRodzaj('INFO');
            $log->setStatusName($name);
            $log->setCreatedAt($now);
            $log->setAddTimeGm($now);
            $log->save();
        }

        //aadd info about save to admin log
        $gmdate = gmdate("Y-m-d H:i:s");
        $admin_l = new AdminLog();
        $admin_l->setExtraInfo('Change role : ' . $name);
        $admin_l->setRodzaj('INFO');
        $admin_l->setAddTimeGm($gmdate);
        $admin_l->save();


        $last_role_id = $role->getId();

        if (!empty($last_role_id)) {

            //save to possible views

            $possible_views = PossibleViewsTable::getInstance()->findAll();

            //save to user views
            if ($possible_views) {
                foreach ($possible_views as $view) {

                    $user_view_up = UserViewsTable::getInstance()->findBySql("user_id = " . $customer . " "
                            . " AND view_id = " . (int) $view->id . " "
                            . " AND role_id = " . $last_role_id);




                    if ($user_view_up->count() == 0)
                        $user_view = new UserViews();
                    else
                        $user_view = UserViewsTable::getInstance()->findOneBy("id", $user_view_up[0]['id']);

                    $user_view->setRoleId($last_role_id);
                    $user_view->setUserId($customer);
                    $user_view->setViewId($view->id);
                    $user_view->setAddedBy(time());
                    $user_view->setCreatedAt(date("Y-m-d H:i:s"));


                    $user_view->save();
                }
            }

            //save custom role id            
            if (!empty($customer)) {
                $user_id = (int) $customer;
                $currUser = sfGuardUserTable::getInstance()->findBy("client_id", $user_id);

                foreach ($currUser as $user) {
                    //$user->setCustomRoleId($last_role_id);
                    //$user->save();
                }
            } else {
                //$user_id = (int) $_SESSION['symfony/user/sfUser/attributes']['symfony/user/sfUser/attributes']['user_id'];
                //$currUser = sfGuardUserTable::getInstance()->findOneBy("id", $user_id);
                //$currUser->setCustomRoleId($last_role_id);
                //$currUser->save();
            }

            //var_dump($currUser);die;
        }

        echo json_encode(['success' => 'Role was saved successfully']);
        return sfView::NONE;
    }*/
}
