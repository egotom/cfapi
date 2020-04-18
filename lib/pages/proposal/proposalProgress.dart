import 'package:cfapi/pages/proposal/proposalDetail.dart';
import 'package:flutter/material.dart';
import 'package:cfapi/services/score.dart';
import 'package:date_range_picker/date_range_picker.dart' as DateRagePicker;
import 'package:flutter_slidable/flutter_slidable.dart';

class ProposalProgress extends StatefulWidget {
  @override
  _ProposalProgressState createState() => _ProposalProgressState();
}

class _ProposalProgressState extends State<ProposalProgress> {
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
          List<DateTime> ldt=[picked[0], picked[1].add(Duration(hours:23,minutes: 59,seconds: 59))];
          getScoreList(range:ldt);
          return picked;
        }
        break;
      default:
        int id=tpIdex==2?0:tpIdex+1;
        int idx=opt==tpClass?id:0;
        setState( () {tpClass=opt; tpIdex=idx;} );
    }    
  }

  @override
  void initState() {
    getScoreList();
    super.initState();
  }
  
  Widget ScoreList( BuildContext context, int index,  AsyncSnapshot snapshot){
    Score score = scores[index];
    return Slidable(
      actionPane: SlidableDrawerActionPane(),
      actionExtentRatio: 0.3,
      actions: <Widget>[
        IconSlideAction(
          caption: '撤销',
          color: Colors.red,
          icon: Icons.cancel,
          onTap: () async{
            bool ok= await Score.remove(score.id);
            if(ok)
              setState(() {
                scores.remove(score);
              });
          },
        ),
        
      ],
      secondaryActions: <Widget>[        
        IconSlideAction(
          caption: '详情',
          color: Colors.blue,
          icon: Icons.more_horiz,
          onTap: () {
            Navigator.push(context,MaterialPageRoute(builder: (BuildContext context) =>proposalDetail(score)));
          },
        ),
      ],
      child: ListTile(
        title: Text('提交：${score.tname}  奖扣：${score.classify} ${score.score}'),
        isThreeLine: false,
        leading: score.state=='提交成功'?
          CircleAvatar(
            child: Icon(Icons.hourglass_empty)
          ): 
          CircleAvatar(
            backgroundColor: Colors.red,
            child: Icon(Icons.report_problem)
          ),
        subtitle: Text(
          score.description,
          maxLines: 2,
          overflow: TextOverflow.ellipsis,
        ),
        onTap: () {
          Navigator.push(context,MaterialPageRoute(builder: (BuildContext context) =>proposalDetail(score)));
        },
      ), 
      key: ObjectKey(score),
    );
  }

  Future<List> future;
  List scores;
  void getScoreList({List<DateTime> range}) async {    
    future = (range!=null)?Score.progress(range:range):Score.progress();
    scores = await future;
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
              expandedHeight: 50.0,
              child: ScoreFilter(scFilter,drge),
            ),
          ),
          FutureBuilder(            
            future:future,
            builder: (context,  snapshot) {
              switch (snapshot.connectionState) {
                case ConnectionState.none:
                case ConnectionState.waiting:
                case ConnectionState.active:
                  return SliverToBoxAdapter(child: Center(child:CircularProgressIndicator()));
                case ConnectionState.done:
                  if (snapshot.hasError)
                    return SliverToBoxAdapter(child: Center(child:Text("error: ${snapshot.error}")));
                  return SliverFixedExtentList(
                    itemExtent: 75.0,
                    delegate: SliverChildBuilderDelegate(
                      (BuildContext context, int index) {
                        int count=snapshot?.data?.length??0;
                        if(index<count && count>0)
                          return ScoreList(context, index, snapshot);
                      },
                    ),
                  );
              }
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

class  ScoreFilter extends StatelessWidget {
  final Function fn;
  String dr='';
  ScoreFilter( @required this.fn, this.dr, { Key key}) : super(key: key);

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
                child: Text('${dr}', style:TextStyle(color:Colors.blue[400])),
                onPressed: ()async{
                  await fn('d');
                }
              ),
              IconButton(
                icon: Icon(Icons.date_range, color:Colors.blue[400]), 
                onPressed: ()async{
                  await fn('d');
                }
              ),
            ],
          ),
        ] 
      ),
    );
  }
}
