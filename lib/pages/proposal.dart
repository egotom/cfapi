import 'package:cfapi/pages/widgets/scoreProposal.dart';
import 'package:flutter/material.dart';
import 'package:cfapi/pages/sideBar.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class Proposal extends StatefulWidget {
  @override
  _ProposalState createState() => _ProposalState();
}

class _ProposalState extends State<Proposal> {
  
  @override
  void initState(){
    super.initState();
  }

  int _selectedIndex = 0;
  final storage = new FlutterSecureStorage();

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      drawer: SideBar('proposal'),
      appBar: AppBar(
        title: Text('成峰积分 － 积分申请',style:TextStyle(fontSize:16)),
        centerTitle: true,
        actions: [
          Row(
            children: <Widget>[
              FlatButton(
                onPressed: () async {
                  await storage.deleteAll();
                  Navigator.pushReplacementNamed(context, '/login');
                },  
                child: Text('退出', style:TextStyle(color:Colors.white)),
              )
            ],
          ),
        ],
      ),

      body: Center(child: <Widget>[
        ScoreProposal(),
        Text('Index 1: 产值申请'),
        Text('Index 2: 审核进度'),
      ].elementAt(_selectedIndex)),
      
      bottomNavigationBar: BottomNavigationBar(
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.star),
            title: Text('积分申请'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.scatter_plot),
            title: Text('产值申请'),
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.timelapse),
            title: Text('审核进度'),
          ),
        ],
        currentIndex: _selectedIndex,
        selectedItemColor: Colors.blue[400],
        onTap:(int index)=>setState(() {_selectedIndex = index;})
      ),
    );
  }
}