#! /bos/usr0/yubink/bin/ruby -I /bos/usr0/yubink/rubylib

require 'qmassage'
require 'set'

#"/bos/usr0/zhuyund/buildIndex_Clueweb09/index"
mqt_queries = QMassage.parse_query(ARGV[0])
trec_queries = QMassage.parse_query(ARGV[1])

outdir = ARGV[2]

cnt = 0
outf = nil
trecqs = Set.new(trec_queries.values)

for qnum, query in mqt_queries.to_a
  if cnt == 10000
    break
  end

  if cnt % 2000 == 0
    if outf
      outf.puts "</parameters>"
      outf.close
    end
    outf = File.new(File.join(outdir, "query.#{cnt/1000}.xml"), "w+")
    outf.puts "<parameters>"
  end

  #nonsingleterms = query.encode(Encoding::UTF_8, Encoding::ISO_8859_1).split.reject {|x| x.length == 1}
  #if !trecqs.include?(nonsingleterms.join(" "))
  if !trecqs.include?(query)
    outf.puts "<query><number>#{qnum}</number><text>#{query}</text></query>"
    cnt += 1
  end
end
outf.puts "</parameters>"
outf.close
