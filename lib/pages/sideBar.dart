import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';

class SideBar extends StatefulWidget {
  SideBar(this._ds);
  final String _ds;
  @override
  _SideBarState createState() => _SideBarState();
}

class _SideBarState extends State<SideBar> {
  User _user;  
  @override
  void initState(){
    setState((){
      _user=Provider.of<User>(context, listen: false);
    });
    super.initState(); 
  }
  
  @override
  Widget build(BuildContext context) {
    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: <Widget>[
          UserAccountsDrawerHeader(            
            accountName:Text('${_user.name}', style: TextStyle(fontWeight: FontWeight.bold,fontSize: 20.0)),
            accountEmail: Text('${_user.team}', style: TextStyle(fontWeight: FontWeight.bold,fontSize: 18.0,)),
            currentAccountPicture: null,
            decoration: BoxDecoration(
              image: DecorationImage(
                image: AssetImage('assets/bg_account_switcher.png'),
                fit: BoxFit.cover
              ),
            ),
          ),
          ListTile(
            title: Text('我的积分',style: TextStyle(fontSize: 18.0, color:widget._ds=='home' ? Colors.blue[400]:Colors.black)),
            leading: Icon(Icons.star, color: widget._ds=='home' ? Colors.blue[400]:Colors.grey[600], size: 23.0),
            onTap: ()=>Navigator.pushReplacementNamed(context, '/home')
          ),
          ListTile(
            title: Text('积分大厅',style: TextStyle(fontSize: 18.0, color:widget._ds=='hall'? Colors.blue[400]:Colors.black)),
            leading: Icon(Icons.account_balance , color: widget._ds=='hall'?Colors.blue[400]:Colors.grey[600], size: 23.0),
            onTap: ()=>Navigator.pushReplacementNamed(context, '/hall')
          ),
          ListTile(
            title: Text('积分申请',style: TextStyle(fontSize: 18.0, color:widget._ds=='proposal'? Colors.blue[400]:Colors.black)),
            leading: Icon(Icons.iso, color: widget._ds=='proposal'? Colors.blue[400]:Colors.grey[600], size: 23.0),
            onTap: ()=>Navigator.pushReplacementNamed(context, '/proposal')
          ),
          ListTile(
            title: Text('积分审批',style: TextStyle(fontSize: 18.0, color:widget._ds=='approve'? Colors.blue[400]:Colors.black)),
            leading: Icon(Icons.school, color: widget._ds=='approve'? Colors.blue[400]:Colors.grey[600], size: 23.0),
            onTap: ()=>Navigator.pushReplacementNamed(context, '/approve')
          ),
          ListTile(
            leading: Icon(Icons.card_giftcard, color: widget._ds=='lottery'? Colors.blue[400]:Colors.grey[600], size: 23.0),
            title: Text('我的奖券',style: TextStyle(fontSize: 18.0, color:widget._ds=='lottery'? Colors.blue[400]:Colors.black)),
            onTap: ()=>Navigator.pushReplacementNamed(context, '/lottery')
          ),
          ListTile(
            leading: Icon(Icons.assignment_ind, color: widget._ds=='account'? Colors.blue[400]:Colors.grey[600], size: 23.0),
            title: Text('账号设置',style: TextStyle(fontSize: 18.0, color:widget._ds=='account'? Colors.blue[400]:Colors.black)),
            onTap: ()=>Navigator.pushReplacementNamed(context, '/account')
          ),
        ],
      ),
    );
  }
}
