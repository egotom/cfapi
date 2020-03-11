import 'package:cfapi/config/theme.dart';
import 'package:flutter/material.dart';
import 'package:cfapi/pages/sideBar.dart';
import 'package:provider/provider.dart';
import 'package:cfapi/services/scoreModel.dart';
import 'package:cfapi/services/authentication.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:date_range_picker/date_range_picker.dart' as DateRagePicker;

class MyScore extends StatefulWidget {
  @override
  _MyScoreState createState() => _MyScoreState();
}

class _MyScoreState extends State<MyScore> {
  String tpClass,drge='';
  int tpIdex=0;

  Future<List<DateTime>> scFilter(opt) async {
    switch(opt){
      case 'd':
        final List<DateTime> picked = await DateRagePicker.showDatePicker(
          context: context,
          initialFirstDate: DateTime.now(),
          initialLastDate: DateTime.now(),
          firstDate: DateTime(2018),
          lastDate: DateTime.now()
        );
        if (picked != null && picked.length == 2) {
          String from = '${picked[0].year-2000}-${picked[0].month}-${picked[0].day}';
          String to = '${picked[1].year-2000}-${picked[1].month}-${picked[1].day}';
          setState(() {drge='$from ~ $to';});
          return picked;
        }
        break;

      default:
        int id=tpIdex==2?0:tpIdex+1;
        int idx=opt==tpClass?id:0;
        setState( () {tpClass=opt; tpIdex=idx;} );
        print(opt);
        print(idx);
    }    
  }

  @override
  void initState() {
    super.initState();
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: EdgeInsets.all(8.0),
      child: CustomScrollView(
        slivers: <Widget>[
          SliverPersistentHeader(
            floating: true,
            delegate: CustomSliverDelegate(
              expandedHeight: 180.0,
              child: ScoreFilter(scFilter,drge),
            ),
          ),
          SliverToBoxAdapter(child: Container(height: 50.0)),
          FutureBuilder(
            future:http('get','score'),
            builder: (context, projectSnap) {
              //if(projectSnap.data['error'] !='0'){
              //  print(projectSnap.data['error']);
              //  return SliverToBoxAdapter(
              //    child: Center(
              //      child: Text(
              //        projectSnap.data['msg'],
              //        style:TextStyle(
              //          color:Colors.red,
              //          fontWeight:FontWeight.bold,
              //          fontSize: 16.0)
              //      )
              //    )
              //  );
              //}
              
              return SliverFixedExtentList(
                itemExtent: 50.0,
                delegate: SliverChildBuilderDelegate(
                  (BuildContext context, int index) {
                    return Container(
                      child: Column(
                        children: <Widget>[
                          Text('id: $index'),
                          Text(projectSnap.data['msg'].toString())
                        ],
                      ),
                    );
                  },
                ),
              );
            }
          ),
        ],
      ),
    );
  }
}

class CustomSliverDelegate extends SliverPersistentHeaderDelegate {
  final double expandedHeight;
  final Widget child;

  CustomSliverDelegate({
    @required this.expandedHeight,
    @required this.child,
  });

  @override
  Widget build(BuildContext context, double shrinkOffset, bool overlapsContent) {
    return child;
  }

  @override
  double get maxExtent => expandedHeight;

  @override
  double get minExtent => expandedHeight;

  @override
  bool shouldRebuild(SliverPersistentHeaderDelegate oldDelegate) {
    return true;
  }
}

class ScoreFilter extends StatefulWidget {
  final fn;
  String dr='';
  ScoreFilter( @required this.fn, this.dr, { Key key}) : super(key: key);
  @override
  _ScoreFilterState createState() => _ScoreFilterState();
}

class _ScoreFilterState extends State<ScoreFilter> {
  @override
  void initState() {
    info();
    super.initState();
  }
  int a=0,aa=0,b=0,bb=0,c=0,cc=0;

  void info({List<DateTime> dt}) async{
    if(dt!=null && dt.length == 2){      
      List dt2=[dt[0],dt[1].add(Duration(hours:23,minutes: 59,seconds: 59))];
      Map rsp=await http('post', 'brief', data:{'range':dt2.toString()});
      if(rsp['error']==0)
        setState(() {
          a=rsp['A+'];
          b=rsp['B+'];
          c=rsp['C+'];
          aa=rsp['A-'];
          bb=rsp['B-'];
          cc=rsp['C-'];
        });      
    }else{
      Map rsp=await http('get', 'brief');
      if(rsp['error']==0)
        setState(() {
          a=rsp['A+'];
          b=rsp['B+'];
          c=rsp['C+'];
          aa=rsp['A-'];
          bb=rsp['B-'];
          cc=rsp['C-'];
        });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      color: Colors.white,
      child: Column(
        children:<Widget>[
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: <Widget>[
              FlatButton(
                child: Text('${widget.dr}', style:TextStyle(color:Colors.blue[400])),
                onPressed: ()async{
                  var dt=await widget.fn('d');
                  if(dt!=null)
                    info(dt: dt);
                }
              ),
              IconButton(
                icon: Icon(Icons.date_range, color:Colors.blue[400]), 
                onPressed: ()async{
                  var dt=await widget.fn('d');
                  if(dt!=null)
                    info(dt: dt);
                }
              ),
            ],
          ),
          Row(
            children: <Widget>[
              Expanded(
                child: Card(
                  color:MyTheme().scdc,
                  child: InkWell(
                    splashColor: Colors.white.withAlpha(80),
                    onTap: ()=>widget.fn('a'),
                    child: Container(                      
                      width: 100,
                      height: 100,
                      padding: EdgeInsets.symmetric(vertical:0.0,horizontal:5.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: <Widget>[
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: <Widget>[
                              Text('A : ' ,style:MyTheme().scdf),
                              Text('A+: ' ,style:MyTheme().scdf),
                              Text('A-: ' ,style:MyTheme().scdf),
                            ],
                          ),
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: <Widget>[
                              Text('${a-aa}' ,style:MyTheme().scdf),
                              Text('$a' ,style:MyTheme().scdf),
                              Text('$aa' ,style:MyTheme().scdf),
                            ],
                          ),
                        ],
                      ),
                    ),
                  )
                ),
              ),
              Expanded(
                child: Card(
                  color:MyTheme().scdc,
                  child: InkWell(
                    splashColor: Colors.white.withAlpha(80),
                    onTap: ()=>widget.fn('b'),
                    child: Container(
                      width: 100,
                      height: 100,
                      padding: EdgeInsets.symmetric(vertical:0.0,horizontal:5.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: <Widget>[
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: <Widget>[
                              Text('B :' ,style:MyTheme().scdf),
                              Text('B+:' ,style:MyTheme().scdf),
                              Text('B-:' ,style:MyTheme().scdf),
                            ],
                          ),
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: <Widget>[
                              Text('${b-bb}' ,style:MyTheme().scdf),
                              Text('$b' ,style:MyTheme().scdf),
                              Text('$bb' ,style:MyTheme().scdf),
                            ],
                          ),
                        ],
                      ),
                    ),
                  )
                ),
              ),
              Expanded(
                child: Card(
                  color:MyTheme().scdc,
                  child: InkWell(
                    splashColor: Colors.white.withAlpha(80),
                    onTap: ()=>widget.fn('c'),
                    child: Container(
                      width: 100,
                      height: 100,
                      padding: EdgeInsets.symmetric(vertical:0.0,horizontal:5.0),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: <Widget>[
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: <Widget>[
                              Text('C :' ,style:MyTheme().scdf),
                              Text('C+:' ,style:MyTheme().scdf),
                              Text('C-:' ,style:MyTheme().scdf),
                            ],
                          ),
                          Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: <Widget>[
                              Text('${c-cc}' ,style:MyTheme().scdf),
                              Text('$c' ,style:MyTheme().scdf),
                              Text('$cc' ,style:MyTheme().scdf),
                            ],
                          ),
                        ],
                      ),
                    ),
                  )
                ),
              ),
            ],
          )
        ] 
      ),
    );
  }
}
