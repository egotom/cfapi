import 'package:cfapi/pages/widgets/tableItem.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:flutter/material.dart';

class MyRank extends StatefulWidget {
  @override
  _MyRankState createState() => _MyRankState();
}

class _MyRankState extends State<MyRank> {
  List lst=[];
  @override
  void initState() {
    rank();
    super.initState();
  }

  rank() async{
    Map<String,dynamic> result= await http('get','rank');
    if(result['error']==0){
      setState(() {lst=result['lst'];});
    }
  }

  @override
  Widget build(BuildContext context) {  
    return SingleChildScrollView(      
      child: Column(
        children: <Widget>[
          SizedBox(height: 20),
          Padding(
            padding: EdgeInsets.only(right:5.0,left:5.0),
            child: Table(
              border: TableBorder.all(),
              children:[['月份','项目','公司排名','团队排名'], ...lst].map<TableRow>((lt){
                return TableRow(                  
                  children:[
                    tableItem(lt[0]), 
                    tableItem(lt[1]), 
                    tableItem(lt[2].toString()), 
                    tableItem(lt[3].toString())
                  ]
                );
              }).toList()
            ),
          ),
        ],
      ),
    );
  }
}