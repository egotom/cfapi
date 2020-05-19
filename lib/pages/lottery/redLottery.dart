import 'package:cfapi/pages/widgets/tableItem.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:flutter/material.dart';
import 'lotteryCard.dart';

class RedLottery extends StatefulWidget {
  @override
  _RedLotteryState createState() => _RedLotteryState();
}

class _RedLotteryState extends State<RedLottery> {
  final TextEditingController _betCtl= TextEditingController(); 
  Map <String,dynamic> my={'avl':0,'usd':0,'bet':0};
  List lst=[];
  @override
  void initState() {
    lottery();
    super.initState();
  }
  lottery() async {
    Map<String,dynamic> result= await http('get','lottery/red');
    if(result['error']==0){
      setState(() {my=result['my'];});
      setState(() {lst=result['lst'];});
    }
  }
  @override
  Widget build(BuildContext context) {
    return SingleChildScrollView(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          LotteryCard(img:'assets/red.jpg', txt1: '可用：${my['avl']} 张',txt2: '已使用：${my['usd']} 张',txt3: '投注：${my['bet']} 张'),
          Container(
            padding: EdgeInsets.fromLTRB(20, 25,20,45),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children:<Widget>[
                Expanded(
                  child: Container(
                    padding: EdgeInsets.only(bottom:15),
                    child: TextField(
                      controller: _betCtl,
                      keyboardType: TextInputType.number,
                      decoration: InputDecoration(hintText: '红券数量'),
                    ),
                  ),
                ),
                SizedBox(width: 100),
                Expanded(
                  child: RaisedButton(
                    onPressed: () async {
                      int qty=int.parse(_betCtl.text);
                      if(qty>my['avl']){
                        Scaffold.of(context).showSnackBar(
                          SnackBar(content: Text("可用红券不足！")),
                        );
                        return;
                      }
                      Map<String,dynamic> result= await http('put','lottery/red',data:{'qty':_betCtl.text});
                      if(result['error']==0){
                        setState(() {my=result['my'];});
                        setState(() {lst=result['lst'];});
                      }
                      Scaffold.of(context).showSnackBar(SnackBar(content: Text(result['msg'])));
                    },
                    color: Colors.blue,
                    child: Text('投注红券',style: TextStyle(fontSize: 16,color: Colors.white)),
                  ),
                )
              ]
            ),
          ),          
          Container(
            padding: EdgeInsets.only(left:16),
            child: Text('红券统计',style: TextStyle(fontWeight:FontWeight.bold))
          ),
          Container(
            padding: EdgeInsets.all(15),
            child: Table(
              border: TableBorder.all(),
              children:[['团队','可用','投注'],...lst].map<TableRow>((lt){
                  return TableRow(
                    children:[
                      tableItem(lt[0]),tableItem(lt[1].toString()),tableItem(lt[2].toString())
                    ]
                  );
                }).toList()
            ),
          )          
        ],
      ),
    );
  }
}